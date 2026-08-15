from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from src.api.dependencies import get_current_admin_user
from src.database import get_db
from src.schemas import SeatCreate, SeatRead
from src.services.seats import SeatService
from src.repositories.seats import SeatRepository
from src.repositories import HallRepository, BookingRepository

router = APIRouter(prefix="/seats", tags=["Места"])



def get_seat_service(db: AsyncSession = Depends(get_db)) -> SeatService:
    return SeatService(SeatRepository(db), HallRepository(db), BookingRepository(db))


class SeatsGenerate(BaseModel):
    rows: int = Field(..., gt=0, le=50)
    seats_per_row: int = Field(..., gt=0, le=50)

@router.get("/", response_model=list[SeatRead])
async def list_seats(
    hall_id: int,
    showtime_id: int | None = None,
    service: SeatService = Depends(get_seat_service),
):
    return await service.list_by_hall(hall_id, showtime_id)

@router.post("/", response_model=SeatRead, status_code=status.HTTP_201_CREATED)
async def create_seat(
    seat_in: SeatCreate,
    service: SeatService = Depends(get_seat_service),
    _admin=Depends(get_current_admin_user),
):
    return await service.create(seat_in)


@router.post("/hall/{hall_id}/generate", response_model=list[SeatRead], status_code=status.HTTP_201_CREATED)
async def generate_seats(
    hall_id: int,
    payload: SeatsGenerate,
    service: SeatService = Depends(get_seat_service),
    _admin=Depends(get_current_admin_user),
):
    return await service.generate_for_hall(hall_id, payload.rows, payload.seats_per_row)


@router.delete("/{seat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_seat(
    seat_id: int,
    service: SeatService = Depends(get_seat_service),
    _admin=Depends(get_current_admin_user),
):
    await service.delete(seat_id)