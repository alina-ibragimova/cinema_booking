
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from repositories import HallRepository, MovieRepository, ShowtimeRepository
from src.api.dependencies import get_current_admin_user
from src.database import get_db
from src.schemas import ShowtimeCreate, ShowtimeRead
from src.services import ShowtimeService
 
router = APIRouter(prefix="/showtimes", tags=["Сеансы"])

def get_showtime_service(db: AsyncSession = Depends(get_db))->ShowtimeService:
    return ShowtimeService(
        repo = ShowtimeRepository(db),
        movie_repo = MovieRepository(db),
        hall_repo = HallRepository(db),
    )
 
@router.get("/", response_model=list[ShowtimeRead])
async def list_showtimes(
    movie_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
    service: ShowtimeRepository=Depends(get_showtime_service),
):
    return await service.list(movie_id=movie_id, skip=skip, limit=limit)
 
 
@router.get("/{showtime_id}", response_model=ShowtimeRead)
async def get_showtime(showtime_id: int, service: ShowtimeRepository=Depends(get_showtime_service),):
    return await service.get(showtime_id)
 
 
@router.post("/", response_model=ShowtimeRead, status_code=status.HTTP_201_CREATED)
async def create_showtime(
    showtime_in: ShowtimeCreate,
    service: ShowtimeRepository=Depends(get_showtime_service),
    _admin=Depends(get_current_admin_user),
):
    return await service.create(showtime_in)
 
 
@router.put("/{showtime_id}", response_model=ShowtimeRead)
async def update_showtime(
    showtime_id: int,
    showtime_in: ShowtimeCreate,
    service: ShowtimeRepository=Depends(get_showtime_service),
    _admin=Depends(get_current_admin_user),
):
    return await service.update(showtime_id, showtime_in)
 
 
@router.delete("/{showtime_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_showtime(
    showtime_id: int,
    service: ShowtimeRepository=Depends(get_showtime_service),
    _admin=Depends(get_current_admin_user),
):
    await service.delete(showtime_id)
 