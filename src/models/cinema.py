from sqlalchemy import String,Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

class Movie(Base):
    __tablename__ = "movie"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    showtimes: Mapped[list["Showtime"]] = relationship(back_populates="movie")

class Hall(Base):
    __tablename__ = "halls"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    showtime: Mapped[list["Showtime"]] = relationship(back_populates="hall")

class Showtime(Base):
    __tablename__ = "showtime"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)