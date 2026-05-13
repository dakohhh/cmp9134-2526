import httpx
from typing import Optional, Annotated
from settings.config import SettingsDep
from app.cache.service import CacheService
from app.common.dependencies import HttpClient
from app.user.models import User, RoleEnum
from app.audit_log.models import ActionEnum
from app.database.config import DatabaseSession
from fastapi import status as HttpStatus, Depends
from app.audit_log.service import AuditLogService
from redis.asyncio import from_url as redis_from_url
from app.audit_log.schemas.create_audit_log_schema import CreateAuditLogSchema
from app.common.exceptions import BadRequestException, ServiceUnavailableException
from .schemas.move_robot_request_schema import MoveRobotRequestSchema, NavigationEnum
from .schemas.get_robot_status_response_schema import GetRobotStatusResponseSchema, Position

class RobotService:
    def __init__(self, session: DatabaseSession, settings: SettingsDep, cache_service: CacheService, audit_log_service: Annotated[AuditLogService, Depends(AuditLogService)], http_client: HttpClient):
        self.session = session
        self.settings = settings
        self.cache_service = cache_service
        self.audit_log_service = audit_log_service
        self.http_client = http_client

    @staticmethod
    def calculate_new_position(position: Position, navigation: NavigationEnum) -> Position:
        if navigation == NavigationEnum.RIGHT:
            return Position(x=position.x + 1 if position.x < 20 else position.x, y=position.y)
        
        if navigation == NavigationEnum.LEFT:
            return Position(x=position.x - 1 if position.x > 0 else position.x, y=position.y)
        
        if navigation == NavigationEnum.UP:
            return Position(x=position.x, y=position.y - 1 if position.y > 0 else position.y)
        
        if navigation == NavigationEnum.DOWN:
            return Position(x=position.x, y=position.y + 1 if position.y < 20 else position.y)
        
        raise ValueError(f"Unhandled navigation direction: {navigation}")

    async def move_robot(self, user: User,  move_robot_request_schema: MoveRobotRequestSchema) -> None:

        if user.role == RoleEnum.VIEWER:
            raise BadRequestException("Viewer's cannot move robot")

        # Get the underlying redis instance or create a new one
        redis = self.cache_service.redis or await redis_from_url(self.settings.REDIS_URL, decode_responses=True)

        lock = await redis.set(name="redis-robot-lock", value=str(user.id), ex=30, nx=True)

        if not lock:
            raise BadRequestException("Robot is currently being operated, try again shortly")

        try:
                # Fetch the current position of the robot
                response = await self.http_client.get(f"{self.settings.BASE_ROBOT_API_URL}/api/status")

                response.raise_for_status()

                get_robot_status_response_schema =  GetRobotStatusResponseSchema.model_validate(response.json())

                new_position = RobotService.calculate_new_position(
                    get_robot_status_response_schema.position,
                    move_robot_request_schema.navigation
                )

                # Update the new position
                response = await self.http_client.post(f"{self.settings.BASE_ROBOT_API_URL}/api/move", json=new_position.model_dump())

                response.raise_for_status()
    
        except httpx.HTTPStatusError as e:
                await redis.delete("redis-robot-lock")
                print("It reached this error")
                if e.response.status_code == HttpStatus.HTTP_500_INTERNAL_SERVER_ERROR:
                    raise ServiceUnavailableException("Robot is temporarily unreachable, try again shortly")
                raise
        
        
        # Release the lock
        await redis.delete("redis-robot-lock")

        # Optionally create a task queue as not to delay/block the UI
        await self.audit_log_service.create_audit_log(
            user, 
            CreateAuditLogSchema(
                action=ActionEnum.COMMAND, 
                navigation_direction=move_robot_request_schema.navigation.value
            )
        )


    async def reset_robot(self, user: User) -> None:
        if user.role == RoleEnum.VIEWER:
            raise BadRequestException("Viewer's cannot reset robot")

        redis = self.cache_service.redis or await redis_from_url(self.settings.REDIS_URL, decode_responses=True)

        lock = await redis.set(name="redis-robot-reset-lock", value=str(user.id), ex=30, nx=True)

        if not lock:
            raise BadRequestException("Robot is currently being reset, try again shortly")

        try:
            response = await self.http_client.post(f"{self.settings.BASE_ROBOT_API_URL}/api/reset")

            response.raise_for_status()

        except httpx.HTTPStatusError as e:
            await redis.delete("redis-robot-reset-lock")
            print("It reached this error")
            if e.response.status_code == HttpStatus.HTTP_500_INTERNAL_SERVER_ERROR:
                raise ServiceUnavailableException("Robot is temporarily unreachable, try again shortly")
            raise
        
        await self.cache_service.delete("map_data")
    
        # Release the lock if exists
        await redis.delete("redis-robot-reset-lock")

        await self.audit_log_service.create_audit_log(
            user, 
            CreateAuditLogSchema(
                action=ActionEnum.RESET_ROBOT, 
                navigation_direction=None,
            )
        )