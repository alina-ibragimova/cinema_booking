from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories import BookingRepository, SeatHoldRepository
from src.schemas import BookingCreate
from src.models import Booking, BookingStatus

SEAT_TAKEN_MESSAGE = "Место уже забронировано"
HOLD_EXPIRED_MESSAGE = "Время на подтверждение истекло, место больше не удерживается."

class BookingService:
    def __init__(self, repo: BookingRepository, hold_repo: SeatHoldRepository):
        self.repo = repo
        self.hold_repo = hold_repo

    async def create_new_booking(self, user_id: int, booking_data: BookingCreate) -> Booking:
        showtime_id, seat_id = booking_data.showtime_id, booking_data.seat_id
        if await self.repo.is_seat_confirmed(showtime_id, seat_id):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=SEAT_TAKEN_MESSAGE)
        if not await self.hold_repo.acquire(showtime_id, seat_id, user_id):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=SEAT_TAKEN_MESSAGE)
        booking_dict = booking_data.model_dump()
        booking_dict["user_id"] = user_id
        booking_dict["status"] = BookingStatus.PENDING
        new_booking = await self.repo.create_booking_safe(booking_dict)
        if new_booking is None:
            await self.hold_repo.release(showtime_id, seat_id)
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=SEAT_TAKEN_MESSAGE)
        return new_booking
 
    async def get_user_bookings(self, user_id: int) -> list[Booking]:
        return await self.repo.get_user_bookings(user_id)
 
    async def confirm_booking(self, user_id: int, booking_id: int) -> Booking:
        booking = await self.repo.get_by_id(booking_id)
        if booking is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Бронирование не найдено")
        if booking.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Это не ваше бронирование")
        if booking.status == BookingStatus.CANCELLED:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Бронирование уже отменено")
        if booking.status == BookingStatus.CONFIRMED:
            return booking
 
        if await self.hold_repo.get_holder(booking.showtime_id, booking.seat_id) != user_id:
            raise HTTPException(status_code=status.HTTP_410_GONE, detail=HOLD_EXPIRED_MESSAGE)
 
        updated = await self.repo.update(booking_id, {"status": BookingStatus.CONFIRMED})
        await self.hold_repo.release(booking.showtime_id, booking.seat_id)
        return updated
 
    async def cancel_booking(self, user_id: int, booking_id: int) -> Booking:
        booking = await self.repo.get_by_id(booking_id)
        if booking is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Бронирование не найдено")
        if booking.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Это не ваше бронирование")
        if booking.status == BookingStatus.CANCELLED:
            return booking
        updated = await self.repo.update(booking_id, {"status": BookingStatus.CANCELLED})
        await self.hold_repo.release(booking.showtime_id, booking.seat_id)
        return updated
    