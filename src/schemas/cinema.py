from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class MovieBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    duration_minutes: int = Field(..., gt=0, description="Длительность должна быть больше 0")

class MovieCreate(MovieBase):
    pass 

class MovieRead(MovieBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class ShowtimeBase(BaseModel):
    start_time: datetime
    movie_id: int
    hall_id: int

class ShowtimeCreate(ShowtimeBase):
    pass

class ShowtimeRead(ShowtimeBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class HallBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)

class HallCreate(HallBase):
    pass  

class HallRead(HallBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
