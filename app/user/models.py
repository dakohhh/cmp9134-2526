from typing import TYPE_CHECKING, Optional
from datetime import datetime
from app.database.models import BaseModel
from sqlmodel import Boolean, Column, Field, Relationship, text

if TYPE_CHECKING:
    from app.token.models import RefreshToken
    from app.transcription.models import Transcription
    from app.speaker.models import Speaker
    from app.speaker_turn.models import SpeakerTurn
    from app.conversation_message.models import ConversationMessage


class User(BaseModel, table=True):
    email: str = Field(unique=True, index=True)
    full_name: Optional[str] = Field(default=None)
    is_staff: bool = Field(sa_column=Column(Boolean, default=False, nullable=False, server_default=text("false")))
    is_super_admin: bool = Field(sa_column=Column(Boolean, default=False, nullable=False, server_default=text("false")))
    sub: str
    is_active: bool = Field(sa_column=Column(Boolean, default=True, nullable=False, server_default=text("true")))
    last_login: Optional[datetime] = Field(default=None)

    refresh_tokens: list["RefreshToken"] = Relationship(back_populates="user")
    transcriptions: list["Transcription"] = Relationship(back_populates="user")
    speakers: list["Speaker"] = Relationship(back_populates="user")
    speaker_turns: list["SpeakerTurn"] = Relationship(back_populates="user")
    conversation_messages: list["ConversationMessage"] = Relationship(back_populates="user")

