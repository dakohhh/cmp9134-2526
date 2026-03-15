from typing import Annotated
from app.user.models import User
from .service import AuditLogService
from app.audit_log.models import AuditLog
from app.common.router import VersionRouter
from app.common.response import HttpResponse
from app.auth.state import require_permission
from fastapi import Depends, status as HttpStatus
from app.common.paginator import PaginationSchema, PaginatorResult

router = VersionRouter(path="audit-log", version="1", tags=["Audit Log"])

@router.get("/", response_model=HttpResponse[PaginatorResult[AuditLog]])
async def get_all_audit_logs(
    paginator_schema: Annotated[PaginationSchema, Depends(PaginationSchema)],
    audit_log_service: Annotated[AuditLogService, Depends(AuditLogService)], 
    _: User = Depends(require_permission())
) -> HttpResponse[PaginatorResult[AuditLog]]:
    results = await audit_log_service.get_all_audit_logs(paginator_schema)
    return HttpResponse(message="Get all Audit Logs", data=results, status_code=HttpStatus.HTTP_200_OK)