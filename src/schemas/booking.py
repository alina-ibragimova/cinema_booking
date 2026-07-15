from pydantic import BaseModel, Field, ConfigDict
from src.models.bookings import BookingStatus

class SeatBase(BaseModel):
    row: int = Field(..., gt=0)
    number: int = Field(..., gt=0)
    hall_id: int

class SeatRead(SeatBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)


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

