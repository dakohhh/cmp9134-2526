from typing import Annotated
from .service import MapService
from app.user.models import User
from app.auth.state import auth_bearer
from app.common.router import VersionRouter
from app.common.response import HttpResponse
from fastapi import Depends, status as HttpStatus
from .schemas.get_map_response import GetMapResponse

router = VersionRouter(path="map", version="1", tags=["Map"])

@router.get("/", response_model=HttpResponse[GetMapResponse])
async def get_map(
    map_service: Annotated[MapService, Depends(MapService)], 
    _: User=Depends(auth_bearer)
) -> HttpResponse[GetMapResponse]:
    results = await map_service.get_map()
    return HttpResponse(message="Get Map", data=results, status_code=HttpStatus.HTTP_200_OK)