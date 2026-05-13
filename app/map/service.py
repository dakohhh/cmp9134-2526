import json
from settings.config import SettingsDep
from app.cache.service import CacheService
from app.common.dependencies import HttpClient
from app.map.schemas.get_map_response import GetMapResponse

class MapService:

    def __init__(self, cache_service: CacheService, settings: SettingsDep, http_client: HttpClient):
        self.cache_service = cache_service
        self.settings = settings
        self.http_client = http_client

    async def get_map(self) -> GetMapResponse:

        cached_map_data = await self.cache_service.get("map_data")

        if not cached_map_data:
            response = await self.http_client.get(url=f"{self.settings.BASE_ROBOT_API_URL}/api/map")
            response.raise_for_status()
            map_data = GetMapResponse.model_validate(response.json())
            await self.cache_service.set("map_data", json.dumps(map_data.model_dump()))

        else:
            map_data = GetMapResponse.model_validate(json.loads(cached_map_data))

        return map_data