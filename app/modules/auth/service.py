from fastapi import HTTPException, status
from app.modules.auth.repository import AuthRepository
from app.modules.auth.models import UserCreate, User
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.config import settings
from datetime import timedelta


class AuthService:
    def __init__(self, repo: AuthRepository):
        self.repo = repo

    async def register_user(self, user_in: UserCreate) -> User:
        # 1. Cek apakah email sudah terdaftar
        existing_user = await self.repo.get_by_email(user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # 2. Hash password dan buat object User
        hashed_password = get_password_hash(user_in.password)
        db_user = User(
            email=user_in.email, hashed_password=hashed_password, name=user_in.name
        )

        # 3. Simpan ke database
        return await self.repo.create(db_user)

    async def authenticate_user(self, email: str, password: str) -> dict:
        # 1. Cari user berdasarkan email
        user = await self.repo.get_by_email(email)

        # 2. Verifikasi password
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 3. Buat Access Token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )

        return {"access_token": access_token, "token_type": "bearer"}
