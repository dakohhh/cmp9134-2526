
from uuid import UUID
from .models import User
from sqlmodel import and_
from typing import Optional
from settings.config import SettingsDep
from app.database.config import DatabaseSession
from app.user.schemas.update_user_schema import UpdateUserSchema
from app.common.exceptions import BadRequestException, NotFoundException
from app.common.paginator import PageNumberPaginator, PaginationSchema, PaginatorResult

class UserService:
    def __init__(self, session: DatabaseSession, settings: SettingsDep):
        self.session = session
        self.settings = settings


    async def get_all_users(self, paginator_schema: PaginationSchema, search: Optional[str] = None) -> PaginatorResult[User]:

        # Build conditions list
        conditions = []
        
        if search:
            conditions.append(User.full_name.ilike(f"%{search}%"))  # type: ignore

        # Combine with and_
        whereclause = (and_(*conditions),) if conditions else None

        paginator = PageNumberPaginator(
            model=User,
            paginator_schema=paginator_schema,
            whereclause=whereclause,
        )

        result = await paginator.apaginate(self.session)

        return result
    

    async def get_user(self, user_id: UUID) -> User:

        user = await self.session.get(User, user_id)

        if not user:
            raise NotFoundException("User not found")

        return user
    

    async def update_user(self, user_id: UUID, update_user_schema: UpdateUserSchema) -> User:

        user = await self.session.get(User, user_id)

        if not user:
            raise NotFoundException("User not found")
        
        if update_user_schema.full_name:
            user.full_name = update_user_schema.full_name

        if update_user_schema.email:
            user.email = update_user_schema.email

        await self.session.commit()

        await self.session.refresh(user)
        
        return user
    

    async def delete_user(self, staff: User, user_id: UUID) -> None:
        user = await self.session.get(User, user_id)
        
        if not user:
            raise NotFoundException("User not found")
        
      
        if staff.id == user.id:
            raise BadRequestException("Operation denied: a user cannot delete their own account.")
        
        
        # Delete user - cascade handles conversations and their documents
        await self.session.delete(user)
        await self.session.commit()