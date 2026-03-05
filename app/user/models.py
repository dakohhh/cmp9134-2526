from enum import Enum
from datetime import datetime
from app.database.models import BaseModel
from typing import TYPE_CHECKING, Optional
from sqlmodel import Boolean, Column, DateTime, Field, Relationship, text

if TYPE_CHECKING:
    from app.token.models import RefreshToken

class RoleEnum(Enum):
    VIEWER = "viewer"
    COMMANDER  = "commander"

class User(BaseModel, table=True):
    email: str = Field(unique=True, index=True)
    full_name: Optional[str] = Field(default=None)
    password: str
    is_super_admin: bool = Field(sa_column=Column(Boolean, default=False, nullable=False, server_default=text("false")))
    is_active: bool = Field(sa_column=Column(Boolean, default=True, nullable=False, server_default=text("true")))
    last_login: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    refresh_tokens: list["RefreshToken"] = Relationship(back_populates="user")
    role: RoleEnum = Field(default=RoleEnum.VIEWER)

