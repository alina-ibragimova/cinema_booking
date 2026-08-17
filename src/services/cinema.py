from __future__ import annotations
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Hall, Movie, Showtime
from src.repositories import HallRepository, MovieRepository, ShowtimeRepository, SeatRepository, SeatHoldRepository, BookingRepository
from src.schemas import HallCreate, MovieCreate, ShowtimeCreate, SeatAvailability


class MovieService:
    def __init__(self, repo: MovieRepository):
        self.repo = repo

    async def create(self, data: MovieCreate) -> Movie:
        return await self.repo.create(data)

    async def get(self, movie_id: int) -> Movie:
        movie = await self.repo.get_by_id(movie_id)
        if movie is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Фильм не найден"
                )
        return movie

    async def list(self, skip: int = 0, limit: int = 100) -> list[Movie]:
        return list(await self.repo.get_all(skip=skip, limit=limit))

    async def update(self, movie_id: int, data: MovieCreate)->Movie:
        movie = await self.repo.update(movie_id,data.model_dump())
        if movie is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Фильм не найден")
        return movie
 
    async def delete(self, movie_id: int) -> None:
        deleted = await self.repo.delete(movie_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Фильм не найден"
                )


 
class HallService:
    def __init__(self, repo: HallRepository):
        self.repo = repo

    async def create(self, data: HallCreate) -> Hall:
        return await self.repo.create(data)
 
    async def get(self, hall_id: int) -> Hall:
        hall = await self.repo.get_by_id(hall_id)
        if hall is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Зал не найден")
        return hall
 
    async def list(self, skip: int = 0, limit: int = 100) -> list[Hall]:
        return list(await self.repo.get_all(skip=skip, limit=limit))
 
    async def update(self, hall_id: int, data: HallCreate) -> Hall:
        hall = await self.repo.update(hall_id, data.model_dump())
        if hall is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Зал не найден")
        return hall
 
    async def delete(self, hall_id: int) -> None:
        deleted = await self.repo.delete(hall_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Зал не найден")
 

class ShowtimeService:
    def __init__(
        self,
        repo: ShowtimeRepository,
        movie_repo: MovieRepository,
        hall_repo: HallRepository,
        seat_repo: SeatRepository,
        booking_repo: BookingRepository,
        hold_repo: SeatHoldRepository,
    ):
        self.repo = repo
        self.movie_repo = movie_repo
        self.hall_repo = hall_repo
        self.seat_repo = seat_repo
        self.booking_repo = booking_repo
        self.hold_repo = hold_repo
 
    async def _validate_refs(self, movie_id: int, hall_id: int) -> None:
        if await self.movie_repo.get_by_id(movie_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Фильм не найден")
        if await self.hall_repo.get_by_id(hall_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Зал не найден")
 
    async def create(self, data: ShowtimeCreate) -> Showtime:
        await self._validate_refs(data.movie_id, data.hall_id)
        return await self.repo.create(data)
 
    async def get(self, showtime_id: int) -> Showtime:
        showtime = await self.repo.get_by_id(showtime_id)
        if showtime is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Сеанс не найден")
        return showtime
 
    async def list(self, movie_id: int | None = None, skip: int = 0, limit: int = 100) -> list[Showtime]:
        if movie_id is not None:
            return await self.repo.get_by_movie(movie_id)
        return list(await self.repo.get_all(skip=skip, limit=limit))
 
    async def update(self, showtime_id: int, data: ShowtimeCreate) -> Showtime:
        await self._validate_refs(data.movie_id, data.hall_id)
        showtime = await self.repo.update(showtime_id, data.model_dump())
        if showtime is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Сеанс не найден")
        return showtime
 
    async def delete(self, showtime_id: int) -> None:
        deleted = await self.repo.delete(showtime_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Сеанс не найден")
 
    async def get_seat_map(self, showtime_id: int) -> List[SeatAvailability]:
        showtime = await self.get(showtime_id)  
        seats = await self.seat_repo.get_by_hall(showtime.hall_id)
        confirmed_ids = await self.booking_repo.get_confirmed_seat_ids(showtime_id)
        held_ids = await self.hold_repo.get_held_seat_ids(showtime_id)
        taken_ids = confirmed_ids | held_ids
        return [
            SeatAvailability(
                id=seat.id,
                row=seat.row,
                number=seat.number,
                hall_id=seat.hall_id,
                is_available=seat.id not in taken_ids,
            )
            for seat in seats
        ]