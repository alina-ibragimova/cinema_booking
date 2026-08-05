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

@pytest.mark.asyncio
async def test_cancel_booking_not_found(service, fake_repo):
    fake_repo.get_by_id.return_value = None
    with pytest.raises(HTTPException) as exc_info:
        await service.cancel_booking(user_id=1, booking_id=999)
    assert exc_info.value.status_code == 404

@pytest.mark.asyncio
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