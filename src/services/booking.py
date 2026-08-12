from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.booking import BookingRepository
from src.schemas.booking import BookingCreate
from src.models.bookings import Booking, BookingStatus

SEAT_TAKEN_MESSAGE = "Место уже забронировано"

class BookingService:
    # @staticmethod
    # async def create_new_booking(session:AsyncSession,user_id:int,booking_data:BookingCreate)->Booking:
    #     repo = BookingRepository(session)
    #     is_taken = await repo.is_seat_taken(
    #         session_id=booking_data.session_id,
    #         seat_number = booking_data.seat_number
    #     )
    #     if is_taken:
    #         raise HTTPException(
    #             status_code=status.HTTP_409_CONFLICT,
    #             detail="К сожалению, это место уже забронировано."
    #         )
    #     booking_dict = booking_data.model_dump()
    #     booking_dict["user_id"] = user_id
    #     booking_dict["status"] = "active"
    #     new_booking = await repo.create_from_dict(booking_dict)
    #     return new_booking

    def __init__(self, repo: BookingRepository):
        self.repo = repo

    async def create_new_booking(self, user_id: int, booking_data: BookingCreate) -> Booking:
        is_taken = await self.repo.is_seat_taken(
            showtime_id=booking_data.showtime_id,
            seat_id = booking_data.seat_id
        )
        if is_taken:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=SEAT_TAKEN_MESSAGE
            )
        booking_dict = booking_data.model_dump()
        booking_dict["user_id"] = user_id
        booking_dict["status"] = BookingStatus.PENDING
        new_booking = await self.repo.create_booking_safe(booking_dict)
        if new_booking is None:
            raise HTTPException(status_code=409, detail="Seat was taken during booking (race condition)")
        return new_booking

    async def get_user_bookings(self, user_id: int) -> list[Booking]:
        return await self.repo.get_user_bookings(user_id)

    async def cancel_booking(self, user_id: int, booking_id: int) -> Booking:
        booking = await self.repo.get_by_id(booking_id)
        if booking is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Бронирование не найдено")
        if booking.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Это не ваше бронирование")
        if booking.status == BookingStatus.CANCELLED:
            return booking
        return await self.repo.update(booking_id, {"status":BookingStatus.CANCELLED})