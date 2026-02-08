from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import Role
from ..schemas.user import UserResponse
from ..middleware.deps import get_current_user
from ..models.user import User

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
@router.get("/", response_model=List[UserResponse])
async def list_users(
    role: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(User)
    if role:
        query = query.join(Role).filter(Role.name == role)
        
    return query.offset(skip).limit(limit).all()
