from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Hall, Movie, Showtime
from src.repositories import HallRepository, MovieRepository, ShowtimeRepository
from src.schemas import HallCreate, MovieCreate, ShowtimeCreate
 
 
# class MovieService:
#     @staticmethod
#     async def create(session: AsyncSession, data: MovieCreate) -> Movie:
#         return await MovieRepository(session).create(data)

#     @staticmethod
#     async def get(session: AsyncSession, movie_id: int) -> Movie:
#         movie = await MovieRepository(session).get_by_id(movie_id)
#         if movie is None:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Фильм не найден"
#                 )
#         return movie

#     @staticmethod
#     async def list(session: AsyncSession, skip: int = 0, limit: int = 100) -> list[Movie]:
#         return list(await MovieRepository(session).get_all(skip=skip, limit=limit))

#     @staticmethod
#     async def update(session: AsyncSession, movie_id: int, data: MovieCreate)->Movie:
#         movie = await MovieRepository(session).update(movie_id,data.model_dump())
#         if movie is None:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Фильм не найден")
#         return movie
 
#     @staticmethod
#     async def delete(session: AsyncSession, movie_id: int) -> None:
#         deleted = await MovieRepository(session).delete(movie_id)
#         if not deleted:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Фильм не найден"
#                 )


 
# class HallService:
#     @staticmethod
#     async def create(session: AsyncSession, data: HallCreate) -> Hall:
#         return await HallRepository(session).create(data)
 
#     @staticmethod
#     async def get(session: AsyncSession, hall_id: int) -> Hall:
#         hall = await HallRepository(session).get_by_id(hall_id)
#         if hall is None:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Зал не найден")
#         return hall
 
#     @staticmethod
#     async def list(session: AsyncSession, skip: int = 0, limit: int = 100) -> list[Hall]:
#         return list(await HallRepository(session).get_all(skip=skip, limit=limit))
 
#     @staticmethod
#     async def update(session: AsyncSession, hall_id: int, data: HallCreate) -> Hall:
#         hall = await HallRepository(session).update(hall_id, data.model_dump())
#         if hall is None:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Зал не найден")
#         return hall
 
#     @staticmethod
#     async def delete(session: AsyncSession, hall_id: int) -> None:
#         deleted = await HallRepository(session).delete(hall_id)
#         if not deleted:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Зал не найден")
 
# class ShowtimeService:
#     @staticmethod
#     async def _validate_refs(session: AsyncSession, movie_id: int, hall_id: int) -> None:
#         if await MovieRepository(session).get_by_id(movie_id) is None:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Фильм не найден"
#                 )
#         if await HallRepository(session).get_by_id(hall_id) is None:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND, 
#                 detail="Зал не найден"
#                 )
        
#     @staticmethod
#     async def create(session: AsyncSession, data: ShowtimeCreate) -> Showtime:
#         await ShowtimeService._validate_refs(session, data.movie_id, data.hall_id)
#         return await ShowtimeRepository(session).create(data)
 
#     @staticmethod
#     async def get(session: AsyncSession, showtime_id: int) -> Showtime:
#         showtime = await ShowtimeRepository(session).get_by_id(showtime_id)
#         if showtime is None:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND, 
#                 detail="Сеанс не найден"
#                 )
#         return showtime
 
#     @staticmethod
#     async def list(
#         session: AsyncSession,
#         movie_id: int | None = None, 
#         skip: int = 0, 
#         limit: int = 100
#     ) -> list[Showtime]:
#         repo = ShowtimeRepository(session)
#         if movie_id is not None:
#             return await repo.get_by_movie(movie_id)
#         return list(await repo.get_all(skip=skip, limit=limit))
 
#     @staticmethod
#     async def update(session: AsyncSession, showtime_id: int, data: ShowtimeCreate) -> Showtime:
#         await ShowtimeService._validate_refs(session, data.movie_id, data.hall_id)
#         showtime = await ShowtimeRepository(session).update(showtime_id, data.model_dump())
#         if showtime is None:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND, 
#                 detail="Сеанс не найден"
#                 )
#         return showtime
 
#     @staticmethod
#     async def delete(session: AsyncSession, showtime_id: int) -> None:
#         deleted = await ShowtimeRepository(session).delete(showtime_id)
#         if not deleted:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND, 
#                 detail="Сеанс не найден"
#                 )


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
    def __init__(self, repo: ShowtimeRepository, movie_repo: MovieRepository, hall_repo: HallRepository):
        self.repo = repo
        self.movie_repo = movie_repo
        self.hall_repo = hall_repo

    async def _validate_refs(self, movie_id: int, hall_id: int) -> None:
        if await self.movie_repo.get_by_id(movie_id) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Фильм не найден"
                )
        if await self.hall_repo.get_by_id(hall_id) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Зал не найден"
                )
        
    async def create(self, data: ShowtimeCreate) -> Showtime:
        await self._validate_refs(data.movie_id, data.hall_id)
        return await self.repo.create(data)
 
    async def get(self, showtime_id: int) -> Showtime:
        showtime = await self.repo.get_by_id(showtime_id)
        if showtime is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Сеанс не найден"
                )
        return showtime
 
    async def list(
        self,
        movie_id: int | None = None, 
        skip: int = 0, 
        limit: int = 100
    ) -> list[Showtime]:
        if movie_id is not None:
            return await self.repo.get_by_movie(movie_id)
        return list(await self.repo.get_all(skip=skip, limit=limit))
 
    async def update(self, showtime_id: int, data: ShowtimeCreate) -> Showtime:
        await self._validate_refs(data.movie_id, data.hall_id)
        showtime = await self.repo.update(showtime_id, data.model_dump())
        if showtime is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Сеанс не найден"
                )
        return showtime
 
    async def delete(self, showtime_id: int) -> None:
        deleted = await self.repo.delete(showtime_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Сеанс не найден"
                )