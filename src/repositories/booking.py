from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories import BaseRepository
from src.models import Booking 
from src.schemas import BookingCreate


class BookingRepository(BaseRepository[Booking, BookingCreate]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=Booking, session=session)

    async def get_user_bookings(self, user_id: int) -> list[Booking]:
        query = select(self.model).where(self.model.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def is_seat_taken(self, session_id: int, seat_number: int) -> bool:
        query = select(self.model).where(
            self.model.session_id == session_id,
            self.model.seat_number == seat_number,
            self.model.status == "active"
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

    async def create_booking_safe(self, data: dict) -> Booking | None:
        try:
            return await self.create_from_dict(data)
        except IntegrityError:
            await self.session.rollback()
            return None