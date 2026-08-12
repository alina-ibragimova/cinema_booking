import pytest
from unittest.mock import AsyncMock
from fastapi import HTTPException
from src.services import BookingService
from src.models import Booking, BookingStatus
from src.schemas import BookingCreate

@pytest.fixture
def fake_repo():
    return AsyncMock()

@pytest.fixture
def service(fake_repo):
    return BookingService(fake_repo)

async def test_cancel_booking_not_found(service, fake_repo):
    fake_repo.get_by_id.return_value = None
    with pytest.raises(HTTPException) as exc_info:
        await service.cancel_booking(user_id=1, booking_id=999)
    assert exc_info.value.status_code == 404

async def test_create_booking_success(service, fake_repo):
    fake_repo.is_seat_taken.return_value = False
    fake_booking = Booking(id=1,user_id=1,showtime_id=1,seat_id=1,status=BookingStatus.PENDING)
    fake_repo.create_booking_safe.return_value=fake_booking
    result = await service.create_new_booking(user_id=1,booking_data=BookingCreate(showtime_id=1,seat_id=1))
    assert result is fake_booking
    fake_repo.create_booking_safe.assert_called_once()
    sent_dict = fake_repo.create_booking_safe.call_args.args[0]
    assert sent_dict["user_id"] == 1
    assert sent_dict["status"] == BookingStatus.PENDING

async def test_create_booking_rejected_if_seat_taken(service, fake_repo):
    fake_repo.is_seat_taken.return_value = True
    with pytest.raises(HTTPException) as exc_info:
        await service.create_new_booking(user_id=1, booking_data=BookingCreate(showtime_id=1,seat_id=1))
    assert exc_info.value.status_code == 409
    fake_repo.create_booking_safe.assert_not_called()

async def test_create_booking_race_condition_returns_409(service, fake_repo):
    fake_repo.is_seat_taken.return_value=False
    fake_repo.create_booking_safe.return_value=None
    with pytest.raises(HTTPException) as exc_info:
        await service.create_new_booking(user_id=1, booking_data=BookingCreate(showtime_id=1, seat_id=1))
    assert exc_info.value.status_code == 409

async def test_cancel_booking_not_found(service, fake_repo):
    fake_repo.get_by_id.return_value = None
    with pytest.raises(HTTPException) as exc_info:
        await service.cancel_booking(user_id=1, booking_id=999)
    assert exc_info.value.status_code == 404
 
async def test_cancel_booking_wrong_owner_forbidden(service, fake_repo):
    booking = Booking(id=1, user_id=2, showtime_id=1, seat_id=1, status=BookingStatus.PENDING)
    fake_repo.get_by_id.return_value = booking
    with pytest.raises(HTTPException) as exc_info:
        await service.cancel_booking(user_id=1, booking_id=1)
    assert exc_info.value.status_code == 403
    fake_repo.update.assert_not_called()
  
async def test_cancel_already_cancelled_is_idempotent(service, fake_repo):
    booking = Booking(id=1, user_id=1, showtime_id=1, seat_id=1, status=BookingStatus.CANCELLED)
    fake_repo.get_by_id.return_value = booking
    result = await service.cancel_booking(user_id=1, booking_id=1)
    assert result is booking
    fake_repo.update.assert_not_called() 

async def test_cancel_booking_success_updates_status(service, fake_repo):
    booking = Booking(id=1, user_id=1, showtime_id=1, seat_id=1, status=BookingStatus.PENDING)
    cancelled = Booking(id=1, user_id=1, showtime_id=1, seat_id=1, status=BookingStatus.CANCELLED)
    fake_repo.get_by_id.return_value = booking
    fake_repo.update.return_value = cancelled
    result = await service.cancel_booking(user_id=1, booking_id=1)
    assert result.status == BookingStatus.CANCELLED
    fake_repo.update.assert_called_once_with(1, {"status": BookingStatus.CANCELLED})
 