import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TMDB_API_KEY = os.getenv("TMDB_API_KEY")
    SARANYU_API_KEY = os.getenv("SARANYU_API_KEY")
    SARANYU_BASE_URL = os.getenv("SARANYU_BASE_URL", "https://api.saranyu.com/v1")
    SARANYU_CALLBACK_URL = os.getenv("SARANYU_CALLBACK_URL")
    DB_CONNECTION_STRING = os.getenv("DB_CONNECTION_STRING")
    
    # Validation Thresholds
    TITLE_MATCH_THRESHOLD = 85
    YEAR_TOLERANCE = 1
    RETRY_DAYS = 3
