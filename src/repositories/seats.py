from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Seat
from src.schemas import SeatCreate


class SeatRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_hall(self, hall_id: int) -> list[Seat]:
        result = await self.session.execute(
            select(Seat).where(Seat.hall_id == hall_id).order_by(Seat.row, Seat.number)
        )
        return list(result.scalars().all())

    async def get_by_id(self, seat_id: int) -> Seat | None:
        result = await self.session.execute(select(Seat).where(Seat.id == seat_id))
        return result.scalar_one_or_none()

    async def create(self, data: SeatCreate) -> Seat:
        seat = Seat(**data.model_dump())
        self.session.add(seat)
        await self.session.commit()
        await self.session.refresh(seat)
        return seat

    async def bulk_create(self, hall_id: int, rows: int, seats_per_row: int) -> list[Seat]:
        seats = [
            Seat(hall_id=hall_id, row=r, number=n)
            for r in range(1, rows + 1)
            for n in range(1, seats_per_row + 1)
        ]
        self.session.add_all(seats)
        await self.session.commit()
        for s in seats:
            await self.session.refresh(s)
        return seats

    async def delete(self, seat_id: int) -> bool:
        seat = await self.get_by_id(seat_id)
        if seat is None:
            return False
        await self.session.delete(seat)
        await self.session.commit()
        return True