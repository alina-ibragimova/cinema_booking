import enum
from sqlalchemy import Integer, ForeignKey, String, Enum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

class BookingStatus(str, enum.Enum):
    PENDING = "pending" 
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled" 

class Seat(Base):
    __tablename__ = "seats"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    row: Mapped[int] = mapped_column(Integer, nullable=False)
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    hall_id: Mapped[int] = mapped_column(ForeignKey("halls.id",ondelete="CASCADE"))
    hall: Mapped["Hall"] = relationship(back_populates="seats")
    bookings: Mapped[list["Booking"]] = relationship(back_populates="seat")
    __table_args__ = (UniqueConstraint("hall_id", "row", "number", name = "uq_hall_row_number"),)

class Booking(Base):
    __tablename__ = "booking"
    id: Mapped[int] = mapped_column(primary_key=True, index = True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    showtime_id: Mapped[int] = mapped_column(ForeignKey("showtimes.id", ondelete="CASCADE"), nullable=False)
    seat_id: Mapped[int] = mapped_column(ForeignKey("seats.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[BookingStatus] = mapped_column(Enum(BookingStatus), default=BookingStatus.PENDING, nullable=False)
    user: Mapped["User"] = relationship(back_populates="bookings")
    showtime: Mapped["Showtime"] = relationship(back_populates="bookings")
    seat: Mapped["Seat"] = relationship(back_populates="bookings")


    