from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories import MovieRepository
from src.api.dependencies import get_current_admin_user
from src.database import get_db
from src.schemas import MovieCreate, MovieRead
from src.services import MovieService
 
router = APIRouter(prefix="/movies", tags=["Фильмы"])

def get_movies_service(db: AsyncSession = Depends(get_db)) -> MovieService:
    # return AuthService(db)
    return MovieService(MovieRepository(db))


 
@router.get("/", response_model=list[MovieRead])
async def list_movies(skip: int = 0, limit: int = 100, service: MovieService=Depends(get_movies_service)):
    return await service.list(skip=skip, limit=limit)
 
 
@router.get("/{movie_id}", response_model=MovieRead)
async def get_movie(movie_id: int, service: MovieService=Depends(get_movies_service)):
    return await service.get(movie_id)
 
 
@router.post("/", response_model=MovieRead, status_code=status.HTTP_201_CREATED)
async def create_movie(
    movie_in: MovieCreate,
    service: MovieService=Depends(get_movies_service),
    _admin=Depends(get_current_admin_user),
):
    return await service.create(movie_in)
 
 
@router.put("/{movie_id}", response_model=MovieRead)
async def update_movie(
    movie_id: int,
    movie_in: MovieCreate,
    service: MovieService=Depends(get_movies_service),
    _admin=Depends(get_current_admin_user),
):
    return await service.update(movie_id, movie_in)
 
 
@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_movie(
    movie_id: int,
    service: MovieService=Depends(get_movies_service),
    _admin=Depends(get_current_admin_user),
):
    await service.delete(movie_id)