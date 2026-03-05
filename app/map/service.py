import json
import httpx
from settings.config import SettingsDep
from app.cache.service import CacheService
from app.map.schemas.get_map_response import GetMapResponse

class MapService:

    def __init__(self, cache_service: CacheService, settings: SettingsDep):
        self.cache_service = cache_service
        self.settings = settings

    async def get_map(self) -> GetMapResponse:

        cached_map_data = await self.cache_service.get("map_data")

        if not cached_map_data:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url=f"{self.settings.BASE_ROBOT_API_URL}/api/map")
                response.raise_for_status()
                map_data = GetMapResponse.model_validate(response.json())
                await self.cache_service.set("map_data", json.dumps(map_data.model_dump()))

        else:
            map_data = GetMapResponse.model_validate(json.loads(cached_map_data))

        return map_data