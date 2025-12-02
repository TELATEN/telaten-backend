from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.modules.auth.models import UserCreate, UserRead, UserLogin
from app.modules.auth.repository import AuthRepository
from app.modules.auth.service import AuthService

router = APIRouter()


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    repo = AuthRepository(db)
    return AuthService(repo)


@router.post("/register", response_model=UserRead)
async def register(
    user_in: UserCreate, service: AuthService = Depends(get_auth_service)
):
    return await service.register_user(user_in)


@router.post("/login")
async def login(
    login_data: UserLogin,
    service: AuthService = Depends(get_auth_service),
):
    return await service.authenticate_user(login_data.email, login_data.password)
