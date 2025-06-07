from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum as DBEnum
from sqlalchemy.orm import relationship
from datetime import datetime
# Adjusted import path assuming database.py is in the same directory (backend)
# For robust imports, especially if models are in a subdirectory, consider relative imports
# from ..database import Base
# However, if 'models' is a module directly under 'backend', and 'database.py' is also under 'backend':
from .database import Base # This might cause circular dependency if database.py imports models.
# Let's try a direct import that should work if PYTHONPATH is set up or running from parent dir
# from backend.database import Base # This is often problematic.

# The most robust way for intra-package imports:
from cx360.backend.database import Base

import enum

# Pydantic models for request/response
from pydantic import BaseModel, EmailStr
# from typing import Literal # Not needed if using the enum directly

class UserRole(str, enum.Enum): # Inherit from str for Pydantic compatibility
    admin = "admin"
    analyst = "analyst"
    agent = "agent"

# SQLAlchemy Model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(DBEnum(UserRole, name="user_role_enum", create_type=True), default=UserRole.agent, nullable=False) # Changed to create_type=True
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Add relationships if needed, e.g., feedbacks
    feedbacks = relationship("Feedback", back_populates="submitter")

# Pydantic models for request/response
class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: UserRole = UserRole.agent

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True # Pydantic V2
        # orm_mode = True # Pydantic V1

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None
