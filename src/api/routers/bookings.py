
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.api.dependencies import get_current_user  
from src.repositories import BookingRepository
from src.schemas import BookingCreate, BookingRead
from src.services import BookingService


router = APIRouter(prefix="/bookings", tags=["Бронирования"])

def get_booking_service(db: AsyncSession = Depends(get_db))->BookingService:
    return BookingService(BookingRepository(db))

# @router.post("/", response_model=BookingRead, status_code=201)
# async def create_booking(
#     booking_in: BookingCreate,
#     db: AsyncSession = Depends(get_db),
#     current_user = Depends(get_current_user)
#     ):

#     booking = await BookingService.create_new_booking(
#             session=db,
#             user_id=current_user.id,
#             booking_data=booking_in
#         )
#     return booking


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

@router.post("/{booking_id}/cancel", response_model=BookingRead)
async def cancel_booking(
    booking_id: int,
    service: BookingService = Depends(get_booking_service),
    current_user = Depends(get_current_user),
):
    return await service.cancel_booking(user_id=current_user.id, booking_id=booking_id)