from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class TrailerSourceType(str, Enum):
    MANUAL = "MANUAL"
    TMDB_YOUTUBE = "TMDB_YOUTUBE"

class Title(BaseModel):
    id: str
    imdb_id: str
    title: str
    release_year: int
    language: str
    trailer_url: Optional[str] = None
    is_automated_trailer: bool = False
    trailer_source_type: Optional[TrailerSourceType] = None
    last_enrichment_attempt: Optional[datetime] = None
    tmdb_id: Optional[str] = None

class TranscodeCallback(BaseModel):
    source_url: str
    hls_url: str
    status: str
    metadata: dict
