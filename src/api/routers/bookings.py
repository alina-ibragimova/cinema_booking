
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db_session
from src.api.dependencies import get_current_user  

from src.schemas.booking import BookingCreate, BookingResponse
from src.services.booking import BookingService


router = APIRouter(prefix="/bookings", tags="Бронирования")

@router.post("/", response_model=BookingResponse, status_code=201)
async def create_booking(
    booking_in: BookingCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
    ):

    booking = await BookingService.create_new_booking(
            session=db,
            user_id=current_user.id,
            booking_data=booking_in
        )
    return booking
