
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
 
from src.api.dependencies import get_current_admin_user
from src.database import get_db
from src.schemas import HallCreate, HallRead
from src.services import HallService
from src.repositories import HallRepository
router = APIRouter(prefix="/halls", tags=["Залы"])
 
def get_hall_service(db: AsyncSession=Depends(get_db))->HallService:
    return HallService(HallRepository(db))

@router.get("/", response_model=list[HallRead])
async def list_halls(skip: int = 0, limit: int = 100, service:HallRepository=Depends(get_hall_service)):
    return await service.list(skip=skip, limit=limit)
 
 
@router.get("/{hall_id}", response_model=HallRead)
async def get_hall(hall_id: int, service:HallRepository=Depends(get_hall_service)):
    return await service.get(hall_id)
 
 
@router.post("/", response_model=HallRead, status_code=status.HTTP_201_CREATED)
async def create_hall(
    hall_in: HallCreate,
    service:HallRepository=Depends(get_hall_service),
    _admin=Depends(get_current_admin_user),
):
    return await service.create(hall_in)
 
 
@router.put("/{hall_id}", response_model=HallRead)
async def update_hall(
    hall_id: int,
    hall_in: HallCreate,
    service:HallRepository=Depends(get_hall_service),
    _admin=Depends(get_current_admin_user),
):
    return await service.update(hall_id, hall_in)
 
 
@router.delete("/{hall_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_hall(
    hall_id: int,
    service:HallRepository=Depends(get_hall_service),
    _admin=Depends(get_current_admin_user),
):
    await service.delete(hall_id)