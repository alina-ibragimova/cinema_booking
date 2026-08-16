from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas import UserCreate
from src.models import User
from src.repositories import UserRepository
from src.core.security import DUMMY_HASH, get_password_hash, verify_password

EMAIL_TAKEN_MESSAGE = "Пользователь с таким email уже зарегистрирован"

class AuthService:
    # @staticmethod
    # async def register_user(session: AsyncSession, user_data: UserCreate) -> User:
    #     repo = UserRepository(session)
    #     existing = await repo.get_by_email(user_data.email)
    #     if existing is not None:
    #         raise HTTPException(
    #             status_code=status.HTTP_409_CONFLICT,
    #             detail=EMAIL_TAKEN_MESSAGE
    #         )
    #     user_dict = {
    #         "email": user_data.email,
    #         "hashed_password": get_password_hash(user_data.password)
    #     }
    #     return await repo.create_from_dict(user_dict)

    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def register_user(self, user_data: UserCreate) -> User:
        existing = await self.repo.get_by_email(user_data.email)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=EMAIL_TAKEN_MESSAGE
            )
        user_dict = {
            "email": user_data.email,
            "hashed_password": get_password_hash(user_data.password)
        }
        new_user = await self.repo.create_user_safe(user_dict)
        if new_user is None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=EMAIL_TAKEN_MESSAGE)
        return new_user

    # @staticmethod
    # async def authenticate_user(session: AsyncSession, email:str, password: str) -> User | None:
    #     repo = UserRepository(session)
    #     user = await repo.get_by_email(email)
    #     if user is None:
    #         verify_password(password, DUMMY_HASH)
    #         return None
    #     if not verify_password(password, user.hashed_password):
    #         return None
    #     return user
    
    async def authenticate_user(self, email:str, password: str) -> User | None:
        user = await self.repo.get_by_email(email)
        if user is None:
            verify_password(password, DUMMY_HASH)
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user