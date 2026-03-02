from fastapi import FastAPI, BackgroundTasks
from src.models import TranscodeCallback
from src.services.enrichment_service import EnrichmentService
import httpx

app = FastAPI()

# Mock CMS Client for demonstration
class MockCMSClient:
    async def get_ranked_titles_missing_trailers(self):
        return [
            {"id": "1", "imdb_id": "tt0111161", "title": "The Shawshank Redemption", "release_year": 1994, "language": "en"}
        ]
    
    async def update_enrichment_attempt(self, title_id: str):
        print(f"Updating last_enrichment_attempt for {title_id}")

    async def update_title_metadata(self, title_id: str, data: dict):
        print(f"Updating metadata for {title_id}: {data}")

    async def finalize_trailer(self, title_id: str, hls_url: str):
        print(f"Finalizing trailer for {title_id}: {hls_url}")

cms_client = MockCMSClient()
enrichment_service = EnrichmentService(cms_client)

@app.post("/callback/saranyu")
async def saranyu_callback(callback: TranscodeCallback):
    if callback.status == "completed":
        title_id = callback.metadata.get("title_id")
        await cms_client.finalize_trailer(title_id, callback.hls_url)
        await cms_client.update_title_metadata(title_id, {
            "is_automated_trailer": True,
            "trailer_source_type": "TMDB_YOUTUBE"
        })
    return {"status": "ok"}

@app.post("/run-enrichment")
async def trigger_enrichment(background_tasks: BackgroundTasks):
    background_tasks.add_task(enrichment_service.process_daily_batch)
    return {"message": "Enrichment process started"}
