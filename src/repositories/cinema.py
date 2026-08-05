from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
 
from src.repositories import BaseRepository
from src.models import Movie, Hall, Showtime
from src.schemas import MovieCreate, HallCreate, ShowtimeCreate
 
 

class MovieRepository(BaseRepository[Movie, MovieCreate]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=Movie, session=session)
 
 
class HallRepository(BaseRepository[Hall, HallCreate]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=Hall, session=session)
 
 
class ShowtimeRepository(BaseRepository[Showtime, ShowtimeCreate]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=Showtime, session=session)

    async def get_by_movie(self, movie_id: int) -> list[Showtime]:
        query = select(self.model).where(self.model.movie_id == movie_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())
 