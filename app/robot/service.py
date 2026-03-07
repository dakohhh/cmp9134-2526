import httpx
from typing import Optional
from settings.config import SettingsDep
from app.database.config import DatabaseSession
from .schemas.move_robot_request_schema import MoveRobotRequestSchema, NavigationEnum
from .schemas.get_robot_status_response_schema import GetRobotStatusResponseSchema, Position

class RobotService:
    def __init__(self, session: DatabaseSession, settings: SettingsDep):
        self.session = session
        self.settings = settings

    async def move_robot(self, move_robot_request_schema: MoveRobotRequestSchema) -> None:
        # self.settings.BASE_ROBOT_API_URL

        # Fetch the current position of the robot
        async with httpx.AsyncClient(base_url=self.settings.BASE_ROBOT_API_URL, timeout=30.0) as client:
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
            raise ValueError(f"Unhandled navigation direction: {move_robot_request_schema.navigation}")

        # Update the new position
        async with httpx.AsyncClient(base_url=self.settings.BASE_ROBOT_API_URL, timeout=30.0) as client:
            
            response = await client.post("/api/move", json=new_position.model_dump())

            response.raise_for_status()