from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext

from backend.models.orm.user import User
from backend.models.schemas.user import UserCreate, UserUpdate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        return self.db.query(User).filter(User.username == username).first()

    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        # Check if email or username already exists
        if self.get_user_by_email(user_data.email):
            raise ValueError("Email already registered")
        if self.get_user_by_username(user_data.username):
            raise ValueError("Username already taken")

        # Create user instance
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=self._get_password_hash(user_data.password),
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            role=user_data.role,
            phone_number=user_data.phone_number,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        try:
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            return db_user
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Error creating user")

    def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user details."""
        db_user = self.get_user(user_id)
        if not db_user:
            return None

        update_data = user_data.model_dump(exclude_unset=True)
        
        # Handle password update separately
        if "password" in update_data:
            update_data["password_hash"] = self._get_password_hash(update_data.pop("password"))

        # Check email uniqueness if being updated
        if "email" in update_data and update_data["email"] != db_user.email:
            if self.get_user_by_email(update_data["email"]):
                raise ValueError("Email already registered")

        # Check username uniqueness if being updated
        if "username" in update_data and update_data["username"] != db_user.username:
            if self.get_user_by_username(update_data["username"]):
                raise ValueError("Username already taken")

        # Update user
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        db_user.updated_at = datetime.utcnow()

        try:
            self.db.commit()
            self.db.refresh(db_user)
            return db_user
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Error updating user")

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user by email and password"""
        user = self.get_user_by_email(email)
        if not user or not user.is_active:
            return None
        if not self.verify_password(password, user.password_hash):
            return None
        return user

    def deactivate_user(self, user_id: int) -> Optional[User]:
        """Deactivate a user account."""
        db_user = self.get_user(user_id)
        if not db_user:
            return None

        db_user.is_active = False
        db_user.updated_at = datetime.utcnow()

        try:
            self.db.commit()
            self.db.refresh(db_user)
            return db_user
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Error deactivating user")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password."""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def _get_password_hash(password: str) -> str:
        """Hash password."""
        return pwd_context.hash(password)
