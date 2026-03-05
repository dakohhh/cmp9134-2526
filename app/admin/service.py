from uuid import UUID
from sqlmodel import select
from app.user.models import User
from settings.config import SettingsDep
from app.database.config import DatabaseSession
from app.common.exceptions import NotFoundException
from app.admin.schemas.update_user_role_schema import UpdateUserRoleSchema

class AdminService:

    def __init__(
            self, 
            settings: SettingsDep,
            session: DatabaseSession,
        ):
        self.settings = settings
        self.session = session

    async def update_user_role(self, user_id: UUID, update_user_role_schema: UpdateUserRoleSchema) -> None:
        user = (await self.session.exec( select(User).where( User.id == user_id ))).first()

        if not user:
            raise NotFoundException("User not found")
        
        user.role = update_user_role_schema.role

        await self.session.commit()




        
