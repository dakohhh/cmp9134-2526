from uuid import UUID
from typing import Optional
from datetime import datetime
from app.user.models import User
from sqlmodel import Field, Relationship, Column,  text, Boolean, DateTime
from app.database.models import BaseModel


class RefreshToken(BaseModel, table=True):
    token: str = Field(unique=True)
    expires_at: datetime = Field(sa_column=Column(DateTime(timezone=True)))
    is_blacklisted: bool = Field(default=False, sa_column=Column(Boolean, default=False, nullable=False, server_default=text("false")))
    user: User = Relationship(back_populates="refresh_tokens")
    user_id: Optional[UUID] = Field(foreign_key="user.id", ondelete="CASCADE")