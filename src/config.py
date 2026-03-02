from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    TMDB_API_KEY: str = "YOUR_TMDB_API_KEY"
    SARANYU_API_KEY: str = "YOUR_SARANYU_API_KEY"
    CMS_API_URL: str = "http://cms-api.internal"
    CALLBACK_URL: str = "http://enrichment-service.internal/callback/saranyu"
    
    TMDB_BASE_URL: str = "https://api.themoviedb.org/3"
    SARANYU_BASE_URL: str = "https://api.saranyu.in/v1"
    
    COOLDOWN_DAYS: int = 3
    MATCH_THRESHOLD: float = 0.9

    class Config:
        env_file = ".env"

settings = Settings()
