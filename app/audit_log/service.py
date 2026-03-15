from .models import AuditLog
from app.user.models import User
from app.database.config import DatabaseSession
from app.common.paginator import PageNumberPaginator, PaginatorResult, PaginationSchema
from .schemas.create_audit_log_schema import CreateAuditLogSchema

class AuditLogService:
    def __init__(self,  session: DatabaseSession) -> None:
        self.session = session

    async def create_audit_log(self, user: User, create_audit_log_schema: CreateAuditLogSchema) -> AuditLog:      
        new_audit_log = AuditLog(
            action=create_audit_log_schema.action,
            navigation_direction=create_audit_log_schema.navigation_direction,
            user_id=user.id
        )
        self.session.add(new_audit_log)

        await self.session.commit()

        await self.session.refresh(new_audit_log)

        return new_audit_log
    

    async def get_all_audit_logs(self, paginator_schema: PaginationSchema) -> PaginatorResult[AuditLog]:
        paginator = PageNumberPaginator(
            model=AuditLog,
            paginator_schema=paginator_schema,
        )

        result = await paginator.apaginate(self.session)

        return result