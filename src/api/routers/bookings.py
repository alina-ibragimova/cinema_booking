
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis

from src.database import get_db
from src.api.dependencies import get_current_user  
from src.repositories import BookingRepository, SeatHoldRepository
from src.schemas import BookingCreate, BookingRead
from src.services import BookingService
from src.redis_client import get_redis
from src.config import settings

router = APIRouter(prefix="/bookings", tags=["Бронирования"])

def get_booking_service(
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis),
) -> BookingService:
    return BookingService(
        BookingRepository(db),
        SeatHoldRepository(redis_client, settings.SEAT_HOLD_SECONDS),
    )

@router.post("/", response_model=BookingRead, status_code=201)
async def create_booking(
    booking_in: BookingCreate,
    service: BookingService = Depends(get_booking_service),
    current_user = Depends(get_current_user)
    ):
    return await service.create_new_booking(
            user_id=current_user.id,
            booking_data=booking_in
        )

@router.get("/me", response_model=list[BookingRead])
async def get_my_bookings(
    service: BookingService = Depends(get_booking_service),
    current_user = Depends(get_current_user),
):
    return await service.get_user_bookings(user_id = current_user.id)

@router.post("/{booking_id}/confirm", response_model=BookingRead)
async def confirm_booking(
    booking_id: int,
    service: BookingService = Depends(get_booking_service),
    current_user = Depends(get_current_user),
):
    return await service.confirm_booking(user_id=current_user.id, booking_id=booking_id)


@router.post("/{booking_id}/cancel", response_model=BookingRead)
async def cancel_booking(
    booking_id: int,
    service: BookingService = Depends(get_booking_service),
    current_user = Depends(get_current_user),
):
    return await service.cancel_booking(user_id=current_user.id, booking_id=booking_id)