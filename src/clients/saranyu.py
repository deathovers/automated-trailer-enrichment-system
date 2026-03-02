import httpx
from src.config import settings

class SaranyuClient:
    def __init__(self):
        self.client = httpx.AsyncClient(base_url=settings.SARANYU_BASE_URL, headers={"Authorization": f"Bearer {settings.SARANYU_API_KEY}"})

    async def request_transcoding(self, youtube_url: str, title_id: str):
        payload = {
            "source_url": youtube_url,
            "format": "HLS",
            "callback_url": settings.CALLBACK_URL,
            "metadata": {"title_id": title_id}
        }
        # Retry logic
        for attempt in range(3):
            try:
                response = await self.client.post("/transcode", json=payload)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt == 2:
                    raise e
                continue
