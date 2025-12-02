from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.modules.business.models import BusinessProfileRead, BusinessProfileCreate, BusinessProfileUpdate
from app.modules.business.repository import BusinessRepository
from app.modules.business.service import BusinessService
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User

router = APIRouter()

# Dependency to get BusinessService
def get_business_service(db: AsyncSession = Depends(get_db)) -> BusinessService:
    repo = BusinessRepository(db)
    return BusinessService(repo)

@router.post("/profile", response_model=BusinessProfileRead)
async def create_business_profile(
    profile_in: BusinessProfileCreate,
    current_user: User = Depends(get_current_user),
    service: BusinessService = Depends(get_business_service)
):
    """Create a new business profile for the current user."""
    return await service.create_profile(current_user.id, profile_in)

@router.get("/profile", response_model=BusinessProfileRead)
async def get_business_profile(
    current_user: User = Depends(get_current_user),
    service: BusinessService = Depends(get_business_service)
):
    """Get the business profile of the current user."""
    return await service.get_profile(current_user.id)

@router.patch("/profile", response_model=BusinessProfileRead)
async def update_business_profile(
    profile_in: BusinessProfileUpdate,
    current_user: User = Depends(get_current_user),
    service: BusinessService = Depends(get_business_service)
):
    """Update the business profile of the current user."""
    return await service.update_profile(current_user.id, profile_in)
