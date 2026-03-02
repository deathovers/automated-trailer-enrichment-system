import httpx
import asyncio
from src.config import settings
from typing import Optional, List, Dict

class TMDBClient:
    def __init__(self):
        self.client = httpx.AsyncClient(base_url=settings.TMDB_BASE_URL, params={"api_key": settings.TMDB_API_KEY})
        self.rate_limit_semaphore = asyncio.Semaphore(40) # 40 requests per 10 seconds roughly

    async def get_tmdb_id_from_imdb(self, imdb_id: str) -> Optional[Dict]:
        async with self.rate_limit_semaphore:
            response = await self.client.get(f"/find/{imdb_id}", params={"external_source": "imdb_id"})
            if response.status_code == 200:
                data = response.json()
                movie_results = data.get("movie_results", [])
                tv_results = data.get("tv_results", [])
                
                if movie_results:
                    return {"id": str(movie_results[0]["id"]), "type": "movie", "data": movie_results[0]}
                if tv_results:
                    return {"id": str(tv_results[0]["id"]), "type": "tv", "data": tv_results[0]}
            return None

    async def get_trailers(self, tmdb_id: str, media_type: str = "movie") -> List[str]:
        async with self.rate_limit_semaphore:
            endpoint = f"/{media_type}/{tmdb_id}/videos"
            response = await self.client.get(endpoint)
            if response.status_code == 200:
                results = response.json().get("results", [])
                trailers = [
                    f"https://www.youtube.com/watch?v={v['key']}"
                    for v in results
                    if v['type'] == 'Trailer' and v['site'] == 'YouTube' and v.get('official', False)
                ]
                return trailers
            return []
