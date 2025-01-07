from datetime import datetime
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext
import uuid
import logging

from backend.models.orm.user import User
from backend.models.schemas.user import UserCreate, UserUpdate

# Configure logging
logger = logging.getLogger(__name__)

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

    def create_guest_user(self) -> User:
        """Create a new guest user with auto-generated credentials."""
        try:
            # Generate unique guest credentials
            timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            guest_username = f"guest_{timestamp}_{unique_id}"
            guest_email = f"{guest_username}@guest.local"
            guest_password = unique_id  # Use unique_id as password
            password_hash = pwd_context.hash(guest_password)

            logger.debug(f"Creating guest user with username: {guest_username}")
            logger.debug(f"Guest user email: {guest_email}")

            # Create guest user instance
            guest_user = User(
                username=guest_username,
                email=guest_email,
                password_hash=password_hash,
                first_name="Guest",
                last_name="User",
                role="customer",
                is_guest=True,
                is_admin=False,  # Explicitly set is_admin for guest users
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            logger.debug(f"Guest user object created: {guest_user.__dict__}")

            self.db.add(guest_user)
            self.db.commit()
            self.db.refresh(guest_user)

            logger.info(f"Guest user created successfully: {guest_user.to_dict()}")
            return guest_user

        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"IntegrityError creating guest user: {str(e)}")
            raise ValueError("Error creating guest user: duplicate key violation")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected error creating guest user: {str(e)}", exc_info=True)
            raise ValueError(f"Error creating guest user: {str(e)}")

    def authenticate_guest(self) -> Tuple[User, str]:
        """Create and authenticate a new guest user, returning the user and their credentials."""
        try:
            logger.debug("Starting guest user authentication process")
            guest_user = self.create_guest_user()
            password = guest_user.username.split('_')[2]  # Get unique_id part
            logger.info(f"Guest user authenticated successfully: {guest_user.email}")
            return guest_user, password
        except Exception as e:
            logger.error(f"Error in guest authentication: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password."""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def _get_password_hash(password: str) -> str:
        """Hash password."""
        return pwd_context.hash(password)
