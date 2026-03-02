import Levenshtein
from src.config import settings

def calculate_confidence_score(cms_title: str, tmdb_title: str, cms_year: int, tmdb_year: int, cms_lang: str, tmdb_lang: str) -> float:
    # Title Match (Levenshtein)
    title_sim = Levenshtein.ratio(cms_title.lower(), tmdb_title.lower())
    
    # Year Match (+/- 1 year)
    year_diff = abs(cms_year - tmdb_year)
    year_score = 1.0 if year_diff == 0 else (0.5 if year_diff == 1 else 0.0)
    
    # Language Match (Exact)
    lang_score = 1.0 if cms_lang.lower() == tmdb_lang.lower() else 0.0
    
    # Weighted average
    score = (title_sim * 0.5) + (year_score * 0.3) + (lang_score * 0.2)
    return score

def is_valid_match(score: float) -> bool:
    return score >= settings.MATCH_THRESHOLD
