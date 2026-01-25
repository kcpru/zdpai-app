import httpx
from uuid import uuid4

from app.core.config import get_settings


class RandomAvatarsProvider:
    MINIAVS = "miniavs"
    BOTTS = "bottts"

    def __init__(self) -> None:
        settings = get_settings()
        self._client = httpx.AsyncClient(
            base_url=settings.random_avatars_base_url)

    async def get_avatar_async(self, avatar_type: str) -> bytes | None:
        seed = str(uuid4())
        url = f"{avatar_type}/svg?seed={seed}"
        resp = await self._client.get(url, timeout=10)
        if resp.status_code != 200:
            return None
        return resp.content
