import asyncio
import bcrypt
from sqlmodel import select
from app.user.models import User, RoleEnum
from app.database.config import get_cli_session

DEFAULT_COMMANDER_EMAIL = "admin@robot.com"
DEFAULT_COMMANDER_PASSWORD = "password"
DEFAULT_COMMANDER_NAME = "Default Commander"


async def seed() -> None:
    async with get_cli_session() as session:
        existing = (await session.exec(select(User).where(User.email == DEFAULT_COMMANDER_EMAIL))).first()

        if existing:
            print(f"Commander already exists: {existing.email}")
            return

        hashed = bcrypt.hashpw(DEFAULT_COMMANDER_PASSWORD.encode(), bcrypt.gensalt()).decode()
        commander = User(
            full_name=DEFAULT_COMMANDER_NAME,
            email=DEFAULT_COMMANDER_EMAIL,
            password=hashed,
            role=RoleEnum.COMMANDER,
            is_active=True,
            is_super_admin=True,
        )
        session.add(commander)
        await session.commit()
        print(f"Default commander created: {DEFAULT_COMMANDER_EMAIL}")


if __name__ == "__main__":
    asyncio.run(seed())
