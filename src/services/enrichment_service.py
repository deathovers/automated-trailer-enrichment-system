import logging
from datetime import datetime, timedelta
from src.clients.tmdb import TMDBClient
from src.clients.saranyu import SaranyuClient
from src.utils.validation import calculate_confidence_score, is_valid_match
from src.models import Title, TrailerSourceType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnrichmentService:
    def __init__(self, cms_client):
        self.tmdb = TMDBClient()
        self.saranyu = SaranyuClient()
        self.cms = cms_client

    async def process_daily_batch(self):
        # 1. Get ranked titles with missing trailers
        titles_to_process = await self.cms.get_ranked_titles_missing_trailers()
        
        for title_data in titles_to_process:
            title = Title(**title_data)
            
            # Cooldown check
            if title.last_enrichment_attempt:
                if datetime.now() < title.last_enrichment_attempt + timedelta(days=3):
                    logger.info(f"Skipping {title.title} due to cooldown.")
                    continue

            try:
                await self.enrich_title(title)
            except Exception as e:
                logger.error(f"Failed to enrich {title.title}: {e}")
                await self.cms.update_enrichment_attempt(title.id)

    async def enrich_title(self, title: Title):
        # 2. Mapping Engine
        tmdb_info = await self.tmdb.get_tmdb_id_from_imdb(title.imdb_id)
        if not tmdb_info:
            logger.warning(f"No TMDB mapping found for {title.title}")
            await self.cms.update_enrichment_attempt(title.id)
            return

        tmdb_id = tmdb_info["id"]
        tmdb_data = tmdb_info["data"]
        media_type = tmdb_info["type"]

        # 3. Validation
        tmdb_title = tmdb_data.get("title") or tmdb_data.get("name")
        tmdb_date = tmdb_data.get("release_date") or tmdb_data.get("first_air_date")
        tmdb_year = int(tmdb_date.split("-")[0]) if tmdb_date else 0
        tmdb_lang = tmdb_data.get("original_language")

        score = calculate_confidence_score(
            title.title, tmdb_title, 
            title.release_year, tmdb_year, 
            title.language, tmdb_lang
        )

        if not is_valid_match(score):
            logger.warning(f"Validation failed for {title.title} (Score: {score})")
            await self.cms.update_enrichment_attempt(title.id)
            return

        # 4. Source Fetching
        trailers = await self.tmdb.get_trailers(tmdb_id, media_type)
        if not trailers:
            logger.warning(f"No trailers found on TMDB for {title.title}")
            await self.cms.update_enrichment_attempt(title.id)
            return

        target_url = trailers[0]

        # 5. Transcoding Pipeline
        await self.saranyu.request_transcoding(target_url, title.id)
        
        # Update TMDB ID in CMS for future
        await self.cms.update_title_metadata(title.id, {"tmdb_id": tmdb_id})
        logger.info(f"Transcoding requested for {title.title}")
