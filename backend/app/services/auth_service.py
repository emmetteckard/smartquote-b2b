from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from ..models.user import User
from ..schemas.user import UserCreate, UserUpdate
from ..utils.security import get_password_hash, verify_password, create_access_token


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_email(self, email: str):
        return self.db.query(User).filter(User.email == email).first()

    def authenticate_user(self, email: str, password: str):
        user = self.get_user_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    def create_user(self, user_in: UserCreate):
        user = self.get_user_by_email(user_in.email)
        if user:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )
        
        db_user = User(
            email=user_in.email,
            password_hash=get_password_hash(user_in.password),
            full_name=user_in.full_name,
            role_id=user_in.role_id,
            client_id=user_in.client_id,
            is_active=user_in.is_active
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
