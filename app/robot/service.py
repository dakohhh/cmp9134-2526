import httpx
from typing import Optional, Annotated
from settings.config import SettingsDep
from app.cache.service import CacheService
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
    def __init__(self, session: DatabaseSession, settings: SettingsDep, cache_service: CacheService, audit_log_service: Annotated[AuditLogService, Depends(AuditLogService)]):
        self.session = session
        self.settings = settings
        self.cache_service = cache_service
        self.audit_log_service = audit_log_service

    async def move_robot(self, user: User,  move_robot_request_schema: MoveRobotRequestSchema) -> None:

        if user.role == RoleEnum.VIEWER:
            raise BadRequestException("Viewer's cannot move robot")

        # Get the underlying redis instance or create a new one
        redis = self.cache_service.redis or await redis_from_url(self.settings.REDIS_URL, decode_responses=True)

        lock = await redis.set(name="redis-robot-lock", value=str(user.id), ex=30, nx=True)

        if not lock:
            raise BadRequestException("Robot is currently being operated, try again shortly")

        async with httpx.AsyncClient(base_url=self.settings.BASE_ROBOT_API_URL, timeout=30.0) as client:
            try:

                # Fetch the current position of the robot
                response = await client.get("/api/status")

                response.raise_for_status()

                get_robot_status_response_schema =  GetRobotStatusResponseSchema.model_validate(response.json())

                new_position: Optional[Position] = None
                if move_robot_request_schema.navigation == NavigationEnum.RIGHT:

                    new_position = Position(
                        x = get_robot_status_response_schema.position.x + 1 if get_robot_status_response_schema.position.x < 20 else get_robot_status_response_schema.position.x, 
                        y = get_robot_status_response_schema.position.y
                    )

                if move_robot_request_schema.navigation == NavigationEnum.LEFT:

                    new_position = Position(
                        x = get_robot_status_response_schema.position.x - 1 if get_robot_status_response_schema.position.x > 0 else get_robot_status_response_schema.position.x, 
                        y = get_robot_status_response_schema.position.y
                    )


                if move_robot_request_schema.navigation == NavigationEnum.UP:

                    new_position = Position( 
                        x = get_robot_status_response_schema.position.x,
                        y = get_robot_status_response_schema.position.y - 1 if  get_robot_status_response_schema.position.y > 0 else get_robot_status_response_schema.position.y
                    )


                if move_robot_request_schema.navigation == NavigationEnum.DOWN:

                    new_position = Position( 
                        x = get_robot_status_response_schema.position.x,
                        y = get_robot_status_response_schema.position.y + 1 if  get_robot_status_response_schema.position.y < 20  else get_robot_status_response_schema.position.y
                    )

                if new_position is None:
                    await redis.delete("redis-robot-lock")
                    raise ValueError(f"Unhandled navigation direction: {move_robot_request_schema.navigation}")
                
                # Update the new position
                response = await client.post("/api/move", json=new_position.model_dump())

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

        async with httpx.AsyncClient(base_url=self.settings.BASE_ROBOT_API_URL, timeout=30.0) as client:
            try:
                # Fetch the current position of the robot
                response = await client.post("/api/reset")

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