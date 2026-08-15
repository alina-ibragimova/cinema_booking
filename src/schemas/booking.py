from pydantic import BaseModel, Field, ConfigDict
from src.models import BookingStatus

class SeatBase(BaseModel):
    row: int = Field(..., gt=0)
    number: int = Field(..., gt=0)
    hall_id: int

class SeatRead(SeatBase):
    id: int
    is_taken: bool = False
    model_config = ConfigDict(from_attributes=True)
    
class SeatCreate(SeatBase):
    pass

class BookingBase(BaseModel):
    showtime_id: int
    seat_id: int


class BookingCreate(BookingBase):
    pass

class BookingRead(BookingBase):
    id: int
    user_id: int
    status: BookingStatus

    model_config = ConfigDict(from_attributes=True)

