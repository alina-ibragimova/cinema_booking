from datetime import datetime
from sqlalchemy import String,Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

class Movie(Base):
    __tablename__ = "movies"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    showtimes: Mapped[list["Showtime"]] = relationship(back_populates="movie")
    bookings: Mapped[list["Booking"]] = relationship(back_populates="user")

class Hall(Base):
    __tablename__ = "halls"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    showtimes: Mapped[list["Showtime"]] = relationship(back_populates="hall")
    seats: Mapped[list["Seat"]] = relationship(back_populates="hall")

class Showtime(Base):
    __tablename__ = "showtime"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id"), nullable=False)
    hall_id: Mapped[int] = mapped_column(ForeignKey("halls.id"), nullable=False)
    movie: Mapped["Movie"] = relationship(back_populates="showtimes")
    hall: Mapped["Hall"] = relationship(back_populates="showtimes")
    bookings: Mapped[list["Booking"]] = relationship(back_populates="showtimes")