from fastapi import APIRouter, Depends, Response, Cookie, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.modules.auth.dependencies import (
    get_current_user,
    get_optional_current_business,
)
from app.modules.auth.models import (
    User,
    UserCreate,
    UserRead,
    UserLogin,
    UserWithBusinessRead,
)
from app.modules.auth.repository import AuthRepository
from app.modules.auth.service import AuthService
from app.modules.business.models import BusinessProfile, BusinessProfileRead
from app.modules.business.repository import BusinessRepository

router = APIRouter()


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    repo = AuthRepository(db)
    return AuthService(repo)


@router.get("/me", response_model=UserWithBusinessRead)
async def read_users_me(
    current_user: User = Depends(get_current_user),
    current_business: BusinessProfile | None = Depends(get_optional_current_business),
    db: AsyncSession = Depends(get_db),
):
    if not current_business and current_user.role == "user":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not have a business profile. Please create one first.",
        )

    business_read = None
    if current_business:
        business_read = BusinessProfileRead.model_validate(current_business)
        if current_business.level_id:
            business_repo = BusinessRepository(db)
            level = await business_repo.get_level(current_business.level_id)
            if level:
                business_read.level_name = level.name

    return UserWithBusinessRead(**current_user.model_dump(), business=business_read)


@router.post("/register", response_model=UserRead)
async def register(
    user_in: UserCreate, service: AuthService = Depends(get_auth_service)
):
    return await service.register_user(user_in)


@router.post("/login")
async def login(
    login_data: UserLogin,
    response: Response,
    service: AuthService = Depends(get_auth_service),
):
    return await service.authenticate_user(
        login_data.email, login_data.password, response
    )


@router.post("/refresh")
async def refresh_token(
    refresh_token: str | None = Cookie(default=None, alias="refresh_token"),
    service: AuthService = Depends(get_auth_service),
):
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing",
        )
    return await service.refresh_access_token(refresh_token)


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="refresh_token")
    return {"message": "Logged out successfully"}
