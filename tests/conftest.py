import pytest
import pytest_asyncio
import redis.asyncio as redis
from httpx2 import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.main import app
from src.models import Base
from src.database import get_db
from src.config import settings
from src.redis_client import get_redis

TEST_DB_URL = "postgresql+asyncpg://test:test@127.0.0.1:5432/cinema_test"

test_engine = create_async_engine(
    TEST_DB_URL, 
    echo=False, 
    connect_args={"ssl": False}
)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

async def override_get_db():
    async with TestSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest_asyncio.fixture(scope="session")
async def test_redis():
    client = redis.from_url(
    settings.REDIS_URL.rsplit("/", 1)[0].replace("localhost", "127.0.0.1") + "/15",
    decode_responses=True
)
    app.dependency_overrides[get_redis] = lambda: client
    
    yield client
    
    await client.aclose()



@pytest_asyncio.fixture
async def db_session():
    async with TestSessionLocal() as session:
        yield session

@pytest_asyncio.fixture(scope="session", autouse=True)
async def _setup_database(test_redis):
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    await test_engine.dispose()
    # await test_redis.aclose()

@pytest_asyncio.fixture(autouse=True)
async def _clean_tables(test_redis):
    async with test_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())
    await test_redis.flushdb()
    yield


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac

@pytest_asyncio.fixture
async def seed_movie_hall_showtime():
    from src.models import Hall, Movie, Showtime, Seat
    from datetime import datetime, timedelta, timezone

    async with TestSessionLocal() as session:
        movie = Movie(title="Тестовый фильм", duration_minutes=120)
        hall = Hall(name="Зал 1")
        session.add_all([movie, hall])
        await session.flush()

        showtime = Showtime(
            start_time=datetime.now(timezone.utc) + timedelta(hours=2),
            movie_id=movie.id,
            hall_id=hall.id,
        )
        seat1 = Seat(row=1, number=1, hall_id=hall.id)
        seat2 = Seat(row=1, number=2, hall_id=hall.id)
        session.add_all([showtime, seat1, seat2])
        
        await session.commit()
        await session.refresh(showtime)
        await session.refresh(seat1)
        await session.refresh(seat2)

        return {
            "movie_id": movie.id,
            "hall_id": hall.id,
            "showtime_id": showtime.id,
            "seat1_id": seat1.id,
            "seat2_id": seat2.id,
        }

@pytest_asyncio.fixture
def register_and_login(client):
    async def _register_and_login(email: str, password: str = "password123") -> str:
        await client.post("/auth/register", json={"email": email, "password": password})
        resp = await client.post("/auth/login", data={"username": email, "password": password})
        return resp.json()["access_token"]

    return _register_and_login

@pytest_asyncio.fixture
def short_ttl_hold_repo(test_redis):
    from src.repositories import SeatHoldRepository
    return SeatHoldRepository(test_redis, ttl_seconds=1)

@pytest_asyncio.fixture
async def redis_client(test_redis):
    return test_redis
