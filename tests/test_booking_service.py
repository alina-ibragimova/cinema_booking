from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from src.models.bookings import Booking, BookingStatus
from src.schemas.booking import BookingCreate
from src.services.booking import BookingService


@pytest.fixture
def fake_repo():
    return AsyncMock()


@pytest.fixture
def fake_hold_repo():
    return AsyncMock()


@pytest.fixture
def service(fake_repo, fake_hold_repo):
    return BookingService(fake_repo, fake_hold_repo)



async def test_create_booking_rejected_if_already_confirmed(service, fake_repo, fake_hold_repo):
    fake_repo.is_seat_confirmed.return_value = True
    with pytest.raises(HTTPException) as exc_info:
        await service.create_new_booking(user_id=1, booking_data=BookingCreate(showtime_id=1, seat_id=1))
    assert exc_info.value.status_code == 409
    fake_hold_repo.acquire.assert_not_called()  # даже не пытаемся холдить, если уже занято постоянно

async def test_create_booking_rejected_if_hold_not_acquired(service, fake_repo, fake_hold_repo):
    fake_repo.is_seat_confirmed.return_value = False
    fake_hold_repo.acquire.return_value = False  # кто-то уже держит место
    with pytest.raises(HTTPException) as exc_info:
        await service.create_new_booking(user_id=1, booking_data=BookingCreate(showtime_id=1, seat_id=1))
    assert exc_info.value.status_code == 409
    fake_repo.create_booking_safe.assert_not_called()


async def test_create_booking_success(service, fake_repo, fake_hold_repo):
    fake_repo.is_seat_confirmed.return_value = False
    fake_hold_repo.acquire.return_value = True
    fake_booking = Booking(id=1, user_id=1, showtime_id=1, seat_id=1, status=BookingStatus.PENDING)
    fake_repo.create_booking_safe.return_value = fake_booking
    result = await service.create_new_booking(user_id=1, booking_data=BookingCreate(showtime_id=1, seat_id=1))
    assert result is fake_booking
    sent_dict = fake_repo.create_booking_safe.call_args.args[0]
    assert sent_dict["user_id"] == 1
    assert sent_dict["status"] == BookingStatus.PENDING


async def test_create_booking_race_condition_releases_hold_and_returns_409(service, fake_repo, fake_hold_repo):
    fake_repo.is_seat_confirmed.return_value = False
    fake_hold_repo.acquire.return_value = True
    fake_repo.create_booking_safe.return_value = None
    with pytest.raises(HTTPException) as exc_info:
        await service.create_new_booking(user_id=1, booking_data=BookingCreate(showtime_id=1, seat_id=1))
    assert exc_info.value.status_code == 409
    fake_hold_repo.release.assert_called_once_with(1, 1)  # захваченный холд обязаны откатить

async def test_confirm_booking_not_found(service, fake_repo):
    fake_repo.get_by_id.return_value = None
    with pytest.raises(HTTPException) as exc_info:
        await service.confirm_booking(user_id=1, booking_id=999)
    assert exc_info.value.status_code == 404


async def test_confirm_booking_wrong_owner(service, fake_repo):
    booking = Booking(id=1, user_id=2, showtime_id=1, seat_id=1, status=BookingStatus.PENDING)
    fake_repo.get_by_id.return_value = booking
    with pytest.raises(HTTPException) as exc_info:
        await service.confirm_booking(user_id=1, booking_id=1)
    assert exc_info.value.status_code == 403


async def test_confirm_cancelled_booking_rejected(service, fake_repo):
    booking = Booking(id=1, user_id=1, showtime_id=1, seat_id=1, status=BookingStatus.CANCELLED)
    fake_repo.get_by_id.return_value = booking
    with pytest.raises(HTTPException) as exc_info:
        await service.confirm_booking(user_id=1, booking_id=1)
    assert exc_info.value.status_code == 409


async def test_confirm_already_confirmed_is_idempotent(service, fake_repo, fake_hold_repo):
    booking = Booking(id=1, user_id=1, showtime_id=1, seat_id=1, status=BookingStatus.CONFIRMED)
    fake_repo.get_by_id.return_value = booking
    result = await service.confirm_booking(user_id=1, booking_id=1)
    assert result is booking
    fake_hold_repo.get_holder.assert_not_called()


async def test_confirm_expired_hold_returns_410(service, fake_repo, fake_hold_repo):
    booking = Booking(id=1, user_id=1, showtime_id=1, seat_id=1, status=BookingStatus.PENDING)
    fake_repo.get_by_id.return_value = booking
    fake_hold_repo.get_holder.return_value = None  # холд истёк
    with pytest.raises(HTTPException) as exc_info:
        await service.confirm_booking(user_id=1, booking_id=1)
    assert exc_info.value.status_code == 410
    fake_repo.update.assert_not_called()


async def test_confirm_rejected_when_hold_now_belongs_to_someone_else(service, fake_repo, fake_hold_repo):
    booking = Booking(id=1, user_id=1, showtime_id=1, seat_id=1, status=BookingStatus.PENDING)
    fake_repo.get_by_id.return_value = booking
    fake_hold_repo.get_holder.return_value = 2 
    with pytest.raises(HTTPException) as exc_info:
        await service.confirm_booking(user_id=1, booking_id=1)
    assert exc_info.value.status_code == 410
    fake_hold_repo.release.assert_not_called()  # ни в коем случае не трогаем чужой холд
    fake_repo.update.assert_not_called()


async def test_confirm_booking_success_updates_status_and_releases_hold(service, fake_repo, fake_hold_repo):
    booking = Booking(id=1, user_id=1, showtime_id=1, seat_id=1, status=BookingStatus.PENDING)
    confirmed = Booking(id=1, user_id=1, showtime_id=1, seat_id=1, status=BookingStatus.CONFIRMED)
    fake_repo.get_by_id.return_value = booking
    fake_hold_repo.get_holder.return_value = 1  # тот же user_id, что подтверждает
    fake_repo.update.return_value = confirmed
    result = await service.confirm_booking(user_id=1, booking_id=1)
    assert result.status == BookingStatus.CONFIRMED
    fake_repo.update.assert_called_once_with(1, {"status": BookingStatus.CONFIRMED})
    fake_hold_repo.release.assert_called_once_with(1, 1)

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


async def test_cancel_already_cancelled_is_idempotent(service, fake_repo, fake_hold_repo):
    booking = Booking(id=1, user_id=1, showtime_id=1, seat_id=1, status=BookingStatus.CANCELLED)
    fake_repo.get_by_id.return_value = booking
    result = await service.cancel_booking(user_id=1, booking_id=1)
    assert result is booking
    fake_repo.update.assert_not_called()
    fake_hold_repo.release.assert_not_called()


async def test_cancel_booking_success_updates_status_and_releases_hold(service, fake_repo, fake_hold_repo):
    booking = Booking(id=1, user_id=1, showtime_id=1, seat_id=1, status=BookingStatus.PENDING)
    cancelled = Booking(id=1, user_id=1, showtime_id=1, seat_id=1, status=BookingStatus.CANCELLED)
    fake_repo.get_by_id.return_value = booking
    fake_repo.update.return_value = cancelled
    result = await service.cancel_booking(user_id=1, booking_id=1)
    assert result.status == BookingStatus.CANCELLED
    fake_repo.update.assert_called_once_with(1, {"status": BookingStatus.CANCELLED})
    fake_hold_repo.release.assert_called_once_with(1, 1)  # место освобождается сразу, не ждём TTL
