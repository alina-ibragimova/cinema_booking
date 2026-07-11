from dataclasses import Field

from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str = Field(min_length = 6)

class UserOut(BaseModel):
    id: int
    username: str
    role: str
    
    model_config = {"from_attributes": True}
