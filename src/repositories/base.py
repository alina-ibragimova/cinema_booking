from typing import Any, Sequence
from sqlalchemy import select, update, delete, insert
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

class BaseRepository[ModelType, SchemaType: BaseModel]:
    def __init__(self, model: type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session
    
    async def get_by_id(self, id: int) -> ModelType | None:
        query = select(self.model).where(self.model.id == id)
        result = await self.session.execute(query)
        return result.scalar_one()
    
    async def get_all(self, skip: int = 0, limit: int= 100) -> Sequence[ModelType]:
        query = select(self.model).offset(skip).limit(limit)
        result= await self.session.execute(query)
        return result.scalars().all()
    
    async def create(self, data: SchemaType) ->ModelType:
        data_dict = data.model_dump()
        query = insert(self.model).values(**data_dict).returning(self.model)
        result = await self.session.execute(query)
        await self.session.commit()
        return result.scalar_one()
    
    async def update(self, id: int, data: dict[str, Any]) -> ModelType | None:
        query = update(self.model).where(self.model.id==id).values(**data).returning(self.model)
        result = await self.session.execute(query)
        await self.session.commit()
        return result.scalars().first()

    async def delete(self, id:int) ->None:
        query = delete(self.model).where(self.model.id==id)
        await self.session.execute(query)
        await self.session.commit()