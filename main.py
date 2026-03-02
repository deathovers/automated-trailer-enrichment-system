import logging
from datetime import datetime
from services.database import DatabaseService
from services.tmdb import TMDBService
from services.saranyu import SaranyuService
from utils.validation import MetadataValidator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def process_enrichment():
    """
    Core orchestration logic for trailer enrichment.
    """
    db = DatabaseService()
    tmdb = TMDBService()
    saranyu = SaranyuService()
    validator = MetadataValidator()

    logger.info("Starting Daily Trailer Enrichment Job")

    # 1. Fetch Ranked Titles missing trailers and eligible for retry
    titles_to_enrich = db.get_pending_titles(limit=1000)
    logger.info(f"Found {len(titles_to_enrich)} titles to process.")
    
    for title in titles_to_enrich:
        try:
            cms_id = title['id']
            imdb_id = title['imdb_id']
            cms_title = title['cms_title']
            cms_year = title['release_year']

            logger.info(f"Processing ID {cms_id}: {cms_title} ({imdb_id})")
            
            # 2. Map IMDb to TMDB
            tmdb_data = tmdb.find_by_imdb_id(imdb_id)
            if not tmdb_data:
                logger.warning(f"No TMDB mapping for {imdb_id}")
                db.mark_as_not_found(cms_id, "No TMDB mapping found")
                continue

            # 3. Validate Metadata
            is_valid = validator.validate(
                cms_title=cms_title,
                tmdb_title=tmdb_data['title'],
                cms_year=cms_year,
                tmdb_year=tmdb_data['release_year']
            )

            if not is_valid:
                logger.warning(f"Validation failed for {cms_title} vs {tmdb_data['title']}")
                db.mark_as_failed(cms_id, "Metadata validation failed (Title/Year mismatch)")
                continue

            # 4. Fetch YouTube Trailer URL
            youtube_url = tmdb.get_trailer_url(tmdb_data['tmdb_id'], tmdb_data['media_type'])
            if not youtube_url:
                logger.warning(f"No trailer found on TMDB for {tmdb_data['tmdb_id']}")
                db.mark_as_not_found(cms_id, "No YouTube trailer found on TMDB")
                continue

            # 5. Trigger Saranyu Transcoding
            job_id = saranyu.trigger_transcode(youtube_url, content_id=cms_id)
            
            if job_id:
                db.update_status(
                    cms_id, 
                    status='PENDING_TRANSCODE',
                    tmdb_id=tmdb_data['tmdb_id'],
                    source='TMDB_SARANYU'
                )
                logger.info(f"Transcoding triggered for {cms_title}. Job ID: {job_id}")
            
        except Exception as e:
            logger.error(f"Critical error processing {title.get('cms_title', 'Unknown')}: {str(e)}")
            db.mark_as_failed(title.get('id'), f"System Error: {str(e)}")

if __name__ == "__main__":
    process_enrichment()
