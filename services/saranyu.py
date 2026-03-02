import requests
import logging
from config import Config

logger = logging.getLogger(__name__)

class SaranyuService:
    def __init__(self):
        self.api_key = Config.SARANYU_API_KEY
        self.base_url = Config.SARANYU_BASE_URL

    def trigger_transcode(self, youtube_url, content_id):
        """
        Sends YouTube URL to Saranyu for HLS transcoding.
        """
        endpoint = f"{self.base_url}/transcode/youtube"
        payload = {
            "url": youtube_url,
            "format": "HLS",
            "callback_url": Config.SARANYU_CALLBACK_URL,
            "external_id": content_id
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            # Placeholder for actual API call
            # response = requests.post(endpoint, json=payload, headers=headers)
            # response.raise_for_status()
            # return response.json().get('job_id')
            
            logger.info(f"MOCK: Triggered Saranyu for {youtube_url}")
            return "mock_job_12345"
        except Exception as e:
            logger.error(f"Saranyu API Error: {str(e)}")
            return None
