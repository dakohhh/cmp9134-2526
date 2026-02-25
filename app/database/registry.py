"""
Central registry for all SQLModel models.

This module imports all models to ensure SQLAlchemy can properly resolve
relationships when using string references in Relationship() fields.

Import this module early in the application lifecycle (e.g., in database config)
to ensure all models are registered before any database operations.
"""

# Import all models to register them with SQLAlchemy
from app.user.models import User  # noqa: F401
from app.token.models import RefreshToken  # noqa: F401

__all__ = [
    "User",
    "RefreshToken",
]
