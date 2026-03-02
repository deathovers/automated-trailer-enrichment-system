import requests
from config import Config

class TMDBService:
    BASE_URL = "https://api.themoviedb.org/3"

    def __init__(self):
        self.api_key = Config.TMDB_API_KEY

    def find_by_imdb_id(self, imdb_id):
        """Maps IMDb ID to TMDB ID and returns basic metadata."""
        url = f"{self.BASE_URL}/find/{imdb_id}"
        params = {
            "api_key": self.api_key,
            "external_source": "imdb_id"
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        # Check movies then tv
        if data.get('movie_results'):
            res = data['movie_results'][0]
            return {
                "tmdb_id": res['id'],
                "media_type": "movie",
                "title": res.get('title') or res.get('original_title'),
                "release_year": self._extract_year(res.get('release_date'))
            }
        elif data.get('tv_results'):
            res = data['tv_results'][0]
            return {
                "tmdb_id": res['id'],
                "media_type": "tv",
                "title": res.get('name') or res.get('original_name'),
                "release_year": self._extract_year(res.get('first_air_date'))
            }
        return None

    def get_trailer_url(self, tmdb_id, media_type):
        """Fetches the best YouTube trailer URL."""
        url = f"{self.BASE_URL}/{media_type}/{tmdb_id}/videos"
        params = {"api_key": self.api_key}
        response = requests.get(url, params=params)
        response.raise_for_status()
        videos = response.json().get('results', [])

        # Filtering logic: YouTube + Trailer
        trailers = [v for v in videos if v['site'] == 'YouTube' and v['type'] == 'Trailer']
        
        if not trailers:
            return None

        # Sort: Official first, then by most recent (or just take first official)
        trailers.sort(key=lambda x: (x.get('official', False), x.get('published_at', '')), reverse=True)
        
        best_video = trailers[0]
        return f"https://www.youtube.com/watch?v={best_video['key']}"

    def _extract_year(self, date_str):
        if date_str:
            return int(date_str.split('-')[0])
        return None
