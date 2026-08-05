from fastapi import APIRouter, status, Depends,HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from src.database import get_db
from src.services.auth import AuthService
from src.repositories import UserRepository
from src.core.security import create_access_token
from src.schemas import UserCreate, UserRead, Token

router = APIRouter(prefix="/auth", tags=["Авторизация"])

def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    # return AuthService(db)
        return AuthService(UserRepository(db))


@router.post("/register",response_model=UserRead,status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
    ):
    return await auth_service.register_user(user_data = user_in)

@router.post("/login",response_model=Token,)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service)
):
    user = await auth_service.authenticate_user(
        email=form_data.username,
        password = form_data.password
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": str(user.id)})
    return Token(access_token=access_token, token_type="bearer")