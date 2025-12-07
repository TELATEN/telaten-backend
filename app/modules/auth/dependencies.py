from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.db.session import get_db
from app.modules.auth.models import User
from app.modules.auth.repository import AuthRepository
from app.modules.business.models import BusinessProfile
from app.modules.business.repository import BusinessRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    repo = AuthRepository(db)

    user = await repo.get_by_id(UUID(user_id))

    if user is None:
        raise credentials_exception

    return user


async def get_optional_current_business(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> BusinessProfile | None:
    repo = BusinessRepository(db)
    return await repo.get_by_user_id(current_user.id)


async def get_current_business(
    current_business: BusinessProfile | None = Depends(get_optional_current_business),
) -> BusinessProfile:
    if not current_business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not have a business profile. Please create one first.",
        )

    return current_business
