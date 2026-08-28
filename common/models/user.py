from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from common.enums import UserRole


class UserCreate(BaseModel):
    username: str = Field(..., min_length=2, max_length=32, pattern=r"^[a-zA-Z0-9_-]+$")
    display_name: str = Field(..., min_length=2, max_length=64)
    password: str = Field(..., min_length=4)
    role: UserRole = UserRole.OPERATOR


class UserResponse(BaseModel):
    id: int
    username: str
    display_name: str
    role: UserRole
    is_online: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    player_id: int
    username: str
    display_name: str
    role: UserRole


class TokenPayload(BaseModel):
    sub: str
    player_id: int
    role: UserRole
