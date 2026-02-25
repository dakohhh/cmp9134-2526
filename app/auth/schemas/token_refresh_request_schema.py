"""Token refresh request schema."""
from pydantic import BaseModel


class TokenRefreshRequestSchema(BaseModel):
    """Request to refresh access token."""

    refresh_token: str
