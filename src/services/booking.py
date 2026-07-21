from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.booking import BookingRepository
from src.schemas.booking import BookingCreate
from src.models.booking import Booking

class BookingService:
    @staticmethod
    async def create_new_booking(session:AsyncSession,user_id:int,booking_data:BookingCreate)->Booking:
        repo = BookingRepository(session)
        is_taken = await repo.is_seat_taken(
            session_id=booking_data.session_id,
            seat_number = booking_data.seat_number
        )
        if is_taken:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="К сожалению, это место уже забронировано."
            )
        booking_dict = booking_data.model_dump()
        booking_dict["user_id"] = user_id
        booking_dict["status"] = "active"
        new_booking = await repo.create_from_dict(booking_dict)
        return new_booking