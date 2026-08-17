from fastapi import HTTPException, status

from src.repositories import SeatRepository, HallRepository, BookingRepository
from src.schemas import SeatCreate, SeatRead
from src.models import Seat

SEAT_NOT_FOUND = "Место не найдено"
HALL_NOT_FOUND = "Зал не найден"


class SeatService:
    def __init__(self, repo: SeatRepository, hall_repo: HallRepository, booking_repo: BookingRepository):
        self.repo = repo
        self.hall_repo = hall_repo
        self.booking_repo = booking_repo

    async def list_by_hall(self, hall_id: int, showtime_id: int | None = None) -> list[SeatRead]:
        if await self.hall_repo.get_by_id(hall_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=HALL_NOT_FOUND)

        seats = await self.repo.get_by_hall(hall_id)

        taken_ids: set[int] = set()
        if showtime_id is not None:
            # taken_ids = await self.booking_repo.get_taken_seat_ids(showtime_id)
            taken_ids = await self.booking_repo.get_confirmed_seat_ids(showtime_id)
        return [
            SeatRead(id=s.id, row=s.row, number=s.number, hall_id=s.hall_id, is_taken=s.id in taken_ids)
            for s in seats
        ]

    async def create(self, data: SeatCreate) -> Seat:
        if await self.hall_repo.get_by_id(data.hall_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=HALL_NOT_FOUND)
        return await self.repo.create(data)

    async def generate_for_hall(self, hall_id: int, rows: int, seats_per_row: int) -> list[Seat]:
        if await self.hall_repo.get_by_id(hall_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=HALL_NOT_FOUND)
        return await self.repo.bulk_create(hall_id, rows, seats_per_row)

    async def delete(self, seat_id: int) -> None:
        deleted = await self.repo.delete(seat_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=SEAT_NOT_FOUND)