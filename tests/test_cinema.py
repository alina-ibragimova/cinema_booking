

from sqlalchemy import select, text
from src.models import User

async def _make_admin(email: str, db_session):
    result = await db_session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user:
        user.is_admin = True
        await db_session.commit()


async def test_list_movies_is_public(client):
    resp = await client.get("/movies/")
    assert resp.status_code == 200
    assert resp.json() == []


async def test_create_movie_requires_admin(client, register_and_login):
    token = await register_and_login("user@example.com")
    resp = await client.post(
        "/movies/", json={"title": "Тест", "duration_minutes": 100},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403


async def test_create_movie_as_admin(client, register_and_login, db_session):
    await register_and_login("admin@example.com")
    await _make_admin("admin@example.com", db_session)
    token = await register_and_login("admin@example.com")

    resp = await client.post(
        "/movies/", json={"title": "Дюна 3", "duration_minutes": 155},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    assert resp.json()["title"] == "Дюна 3"


async def test_get_missing_movie_returns_404(client):
    resp = await client.get("/movies/9999")
    assert resp.status_code == 404


async def test_create_showtime_with_missing_movie_returns_404_not_500(client, register_and_login, db_session):
    await register_and_login("admin@example.com")
    await _make_admin("admin@example.com", db_session)
    token = await register_and_login("admin@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    hall = (await client.post("/halls/", json={"name": "Зал 1"}, headers=headers)).json()

    resp = await client.post(
        "/showtimes/",
        json={"start_time": "2026-09-01T18:00:00Z", "movie_id": 9999, "hall_id": hall["id"]},
        headers=headers,
    )
    assert resp.status_code == 404


async def test_showtime_filter_by_movie(client, register_and_login, db_session):
    await register_and_login("admin@example.com")
    await _make_admin("admin@example.com", db_session)
    token = await register_and_login("admin@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    movie = (await client.post("/movies/", json={"title": "Фильм A", "duration_minutes": 100}, headers=headers)).json()
    other_movie = (await client.post("/movies/", json={"title": "Фильм B", "duration_minutes": 90}, headers=headers)).json()
    hall = (await client.post("/halls/", json={"name": "Зал 1"}, headers=headers)).json()

    await client.post(
        "/showtimes/",
        json={"start_time": "2026-09-01T18:00:00Z", "movie_id": movie["id"], "hall_id": hall["id"]},
        headers=headers,
    )
    await client.post(
        "/showtimes/",
        json={"start_time": "2026-09-01T20:00:00Z", "movie_id": other_movie["id"], "hall_id": hall["id"]},
        headers=headers,
    )

    resp = await client.get(f"/showtimes/?movie_id={movie['id']}")
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["movie_id"] == movie["id"]


async def test_delete_missing_movie_returns_404(client, register_and_login, db_session):
    await register_and_login("admin@example.com")
    await _make_admin("admin@example.com", db_session)
    token = await register_and_login("admin@example.com")

    resp = await client.delete("/movies/9999", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 404