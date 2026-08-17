import redis.asyncio as redis

HOLD_KEY_PREFIX = "hold"


def _hold_key(showtime_id: int, seat_id: int) -> str:
    return f"{HOLD_KEY_PREFIX}:{showtime_id}:{seat_id}"


class SeatHoldRepository:
    def __init__(self, redis_client: redis.Redis, ttl_seconds: int):
        self.redis = redis_client
        self.ttl_seconds = ttl_seconds

    async def acquire(self, showtime_id: int, seat_id: int, user_id: int) -> bool:
        acquired = await self.redis.set(
            _hold_key(showtime_id, seat_id), str(user_id), nx=True, ex=self.ttl_seconds
        )
        return bool(acquired)

    async def release(self, showtime_id: int, seat_id: int) -> None:
        await self.redis.delete(_hold_key(showtime_id, seat_id))

    async def get_holder(self, showtime_id: int, seat_id: int) -> int | None:
        value = await self.redis.get(_hold_key(showtime_id, seat_id))
        return int(value) if value is not None else None

    async def get_held_seat_ids(self, showtime_id: int) -> set[int]:
        pattern = f"{HOLD_KEY_PREFIX}:{showtime_id}:*"
        seat_ids: set[int] = set()
        async for key in self.redis.scan_iter(match=pattern):
            seat_ids.add(int(key.rsplit(":", 1)[1]))
        return seat_ids
