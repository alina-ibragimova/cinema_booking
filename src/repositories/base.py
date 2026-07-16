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
        return result.scalars().first()
    
    