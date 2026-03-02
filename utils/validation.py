import re
from fuzzywuzzy import fuzz
from config import Config

class MetadataValidator:
    def validate(self, cms_title, tmdb_title, cms_year, tmdb_year):
        """
        Validates if the TMDB result matches the CMS metadata.
        """
        # 1. Title Validation (Fuzzy Match)
        title_score = fuzz.token_sort_ratio(
            self._normalize(cms_title), 
            self._normalize(tmdb_title)
        )
        
        if title_score < Config.TITLE_MATCH_THRESHOLD:
            return False

        # 2. Year Validation (Tolerance)
        if cms_year and tmdb_year:
            if abs(cms_year - tmdb_year) > Config.YEAR_TOLERANCE:
                return False
        
        return True

    def _normalize(self, text):
        if not text:
            return ""
        # Lowercase and remove special characters
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s]', '', text)
        return text.strip()
