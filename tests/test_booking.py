async def test_list_my_bookings_empty(client, register_and_login):
    token = await register_and_login("alice@example.com")
    resp = await client.get("/bookings/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json() == []


async def test_create_booking_success(client, seed_movie_hall_showtime, register_and_login):
    data = seed_movie_hall_showtime
    token = await register_and_login("alice@example.com")
    resp = await client.post(
        "/bookings/",
        json={"showtime_id": data["showtime_id"], "seat_id": data["seat1_id"]},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    assert resp.json()["status"] == "pending"


async def test_create_booking_seat_already_taken(client, seed_movie_hall_showtime, register_and_login):
    data = seed_movie_hall_showtime
    alice_token = await register_and_login("alice@example.com")
    bob_token = await register_and_login("bob@example.com")
    booking = {"showtime_id": data["showtime_id"], "seat_id": data["seat1_id"]}

    r1 = await client.post("/bookings/", json=booking, headers={"Authorization": f"Bearer {alice_token}"})
    assert r1.status_code == 201

    r2 = await client.post("/bookings/", json=booking, headers={"Authorization": f"Bearer {bob_token}"})
    assert r2.status_code == 409


async def test_create_booking_without_token(client, seed_movie_hall_showtime):
    data = seed_movie_hall_showtime
    resp = await client.post(
        "/bookings/", json={"showtime_id": data["showtime_id"], "seat_id": data["seat1_id"]}
    )
    assert resp.status_code == 401


async def test_cancel_booking_by_owner(client, seed_movie_hall_showtime, register_and_login):
    data = seed_movie_hall_showtime
    token = await register_and_login("alice@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    booking = (await client.post(
        "/bookings/", json={"showtime_id": data["showtime_id"], "seat_id": data["seat1_id"]}, headers=headers
    )).json()

    resp = await client.post(f"/bookings/{booking['id']}/cancel", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "cancelled"


async def test_cancel_booking_by_someone_else_forbidden(client, seed_movie_hall_showtime, register_and_login):
    data = seed_movie_hall_showtime
    alice_headers = {"Authorization": f"Bearer {await register_and_login('alice@example.com')}"}
    bob_headers = {"Authorization": f"Bearer {await register_and_login('bob@example.com')}"}
    booking = (await client.post(
        "/bookings/", json={"showtime_id": data["showtime_id"], "seat_id": data["seat1_id"]}, headers=alice_headers
    )).json()

    resp = await client.post(f"/bookings/{booking['id']}/cancel", headers=bob_headers)
    assert resp.status_code == 403


async def test_cancel_nonexistent_booking(client, register_and_login):
    token = await register_and_login("alice@example.com")
    resp = await client.post("/bookings/9999/cancel", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 404


async def test_cancel_is_idempotent(client, seed_movie_hall_showtime, register_and_login):
    data = seed_movie_hall_showtime
    token = await register_and_login("alice@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    booking = (await client.post(
        "/bookings/", json={"showtime_id": data["showtime_id"], "seat_id": data["seat1_id"]}, headers=headers
    )).json()

    await client.post(f"/bookings/{booking['id']}/cancel", headers=headers)
    resp = await client.post(f"/bookings/{booking['id']}/cancel", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "cancelled"


async def test_cancel_frees_seat_for_other_users(client, seed_movie_hall_showtime, register_and_login):
    data = seed_movie_hall_showtime
    alice_headers = {"Authorization": f"Bearer {await register_and_login('alice@example.com')}"}
    bob_headers = {"Authorization": f"Bearer {await register_and_login('bob@example.com')}"}
    booking_payload = {"showtime_id": data["showtime_id"], "seat_id": data["seat1_id"]}

    booking = (await client.post("/bookings/", json=booking_payload, headers=alice_headers)).json()
    await client.post(f"/bookings/{booking['id']}/cancel", headers=alice_headers)

    resp = await client.post("/bookings/", json=booking_payload, headers=bob_headers)
    assert resp.status_code == 201






async def test_confirm_booking_by_owner(client, seed_movie_hall_showtime, register_and_login):
    data = seed_movie_hall_showtime
    token = await register_and_login("alice@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    booking = (await client.post(
        "/bookings/", json={"showtime_id": data["showtime_id"], "seat_id": data["seat1_id"]}, headers=headers
    )).json()

    resp = await client.post(f"/bookings/{booking['id']}/confirm", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "confirmed"


async def test_confirm_booking_by_someone_else_forbidden(client, seed_movie_hall_showtime, register_and_login):
    data = seed_movie_hall_showtime
    alice_headers = {"Authorization": f"Bearer {await register_and_login('alice@example.com')}"}
    bob_headers = {"Authorization": f"Bearer {await register_and_login('bob@example.com')}"}
    booking = (await client.post(
        "/bookings/", json={"showtime_id": data["showtime_id"], "seat_id": data["seat1_id"]}, headers=alice_headers
    )).json()
    resp = await client.post(f"/bookings/{booking['id']}/confirm", headers=bob_headers)
    assert resp.status_code == 403


async def test_second_user_blocked_while_hold_is_active(client, seed_movie_hall_showtime, register_and_login):
    data = seed_movie_hall_showtime
    alice_headers = {"Authorization": f"Bearer {await register_and_login('alice@example.com')}"}
    bob_headers = {"Authorization": f"Bearer {await register_and_login('bob@example.com')}"}
    payload = {"showtime_id": data["showtime_id"], "seat_id": data["seat1_id"]}
    r1 = await client.post("/bookings/", json=payload, headers=alice_headers)
    assert r1.status_code == 201
    r2 = await client.post("/bookings/", json=payload, headers=bob_headers)
    assert r2.status_code == 409


async def test_confirm_after_hold_expired_returns_410(client, seed_movie_hall_showtime, register_and_login, redis_client):
    data = seed_movie_hall_showtime
    token = await register_and_login("alice@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    booking = (await client.post(
        "/bookings/", json={"showtime_id": data["showtime_id"], "seat_id": data["seat1_id"]}, headers=headers
    )).json()
    await redis_client.delete(f"hold:{data['showtime_id']}:{data['seat1_id']}")
    resp = await client.post(f"/bookings/{booking['id']}/confirm", headers=headers)
    assert resp.status_code == 410


async def test_seat_available_again_after_hold_expires_even_with_stale_pending_row(
    client, seed_movie_hall_showtime, register_and_login, redis_client
):
    data = seed_movie_hall_showtime
    alice_headers = {"Authorization": f"Bearer {await register_and_login('alice@example.com')}"}
    bob_headers = {"Authorization": f"Bearer {await register_and_login('bob@example.com')}"}
    payload = {"showtime_id": data["showtime_id"], "seat_id": data["seat1_id"]}
    await client.post("/bookings/", json=payload, headers=alice_headers)
    await redis_client.delete(f"hold:{data['showtime_id']}:{data['seat1_id']}")  # холд "истёк"
    seats = (await client.get(f"/showtimes/{data['showtime_id']}/seats")).json()
    freed_seat = next(s for s in seats if s["id"] == data["seat1_id"])
    assert freed_seat["is_available"] is True
    resp = await client.post("/bookings/", json=payload, headers=bob_headers)
    assert resp.status_code == 201


async def test_confirmed_booking_shown_as_taken_on_seat_map(client, seed_movie_hall_showtime, register_and_login):
    data = seed_movie_hall_showtime
    token = await register_and_login("alice@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    booking = (await client.post(
        "/bookings/", json={"showtime_id": data["showtime_id"], "seat_id": data["seat1_id"]}, headers=headers
    )).json()
    await client.post(f"/bookings/{booking['id']}/confirm", headers=headers)
    seats = (await client.get(f"/showtimes/{data['showtime_id']}/seats")).json()
    booked_seat = next(s for s in seats if s["id"] == data["seat1_id"])
    assert booked_seat["is_available"] is False
