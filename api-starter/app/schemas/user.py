# Author: Ck.epsilon & Chaos (AI Programming Assistant)
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional


# ---------------------------------------------------------------------------
# Request Schemas
# ---------------------------------------------------------------------------

class UserRegister(BaseModel):
    """Payload for user registration."""
    email: EmailStr
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=6, max_length=128)

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Username must be alphanumeric (underscore and hyphen allowed)")
        return v


class UserLogin(BaseModel):
    """Payload for user login."""
    email: EmailStr
    password: str


class TokenRefresh(BaseModel):
    """Payload for token refresh."""
    refresh_token: str


# ---------------------------------------------------------------------------
# Response Schemas
# ---------------------------------------------------------------------------

class Token(BaseModel):
    """JWT token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Public user profile (no password)."""
    id: str
    email: str
    username: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    """Fields a user can update on their own profile."""
    username: Optional[str] = Field(default=None, min_length=3, max_length=100)
