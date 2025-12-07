"""
Service layer orchestrating scraping operations.
Implements business logic and coordinates between components.
"""
from typing import Optional

from config.settings import settings
from models import CharacterData, ScraperResult
from repositories import CharacterRepository
from scrapers import Game8Scraper, DuckDuckGoSearcher
from services.race_matcher import RaceMatcher
from utils import HTTPClient, get_logger


logger = get_logger(__name__)


class ScraperService:
    """
    Main service orchestrating scraping operations.
    Coordinates character lookup, scraping, and race matching.
    """
    
    def __init__(
        self,
        character_repo: Optional[CharacterRepository] = None,
        http_client: Optional[HTTPClient] = None
    ):
        """
        Initialize scraper service with dependencies.
        
        Args:
            character_repo: Character repository (creates new if None)
            http_client: HTTP client (creates new if None)
        """
        self.character_repo = character_repo or CharacterRepository()
        self.http_client = http_client or HTTPClient()
        self._owns_client = http_client is None
        
        # Initialize components
        self.game8_scraper = Game8Scraper(self.http_client)
        self.searcher = DuckDuckGoSearcher(self.http_client)
        self.race_matcher = RaceMatcher(self.http_client)
        
        logger.info("ScraperService initialized")
    
    def get_character_events(self, query: Optional[str] = None) -> ScraperResult:
        """
        Main method to get character events.
        Resolves URL, scrapes data, matches races.
        
        Args:
            query: Character name or search query (uses default URL if None)
        
        Returns:
            ScraperResult with success status and data or error
        """
        try:
            logger.info(f"Getting character events for query: {query or '(default)'}")
            
            # Step 1: Resolve URL
            url = self._resolve_url(query)
            logger.info(f"Resolved URL: {url}")
            
            # Step 2: Scrape character data
            character_data = self.game8_scraper.scrape(url)
            
            # Step 3: Match races in events
            if character_data.events:
                matching_races = self.race_matcher.find_matching_races(
                    character_data.events
                )
                character_data.matching_races = matching_races
            
            logger.info(
                f"Successfully processed character: {len(character_data.events)} events, "
                f"{len(character_data.matching_races)} race matches"
            )
            
            return ScraperResult(success=True, data=character_data)
        
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to get character events: {error_msg}", exc_info=True)
            return ScraperResult(success=False, error=error_msg)
    
    def _resolve_url(self, query: Optional[str]) -> str:
        """
        Resolve character query to Game8 URL.
        Tries repository lookup first, then search as fallback.
        
        Args:
            query: Character name or search query
        
        Returns:
            Full Game8 URL
        
        Raises:
            Exception: If URL cannot be resolved
        """
        # Use default URL if no query
        if not query:
            default_url = f"{settings.GAME8_BASE_URL}/536317"
            logger.debug(f"No query provided, using default URL: {default_url}")
            return default_url
        
        # Try repository lookup (fuzzy matching)
        character = self.character_repo.search(query)
        
        if character:
            logger.info(f"Found character in repository: {character.name}")
            return character.url
        
        # Fallback to DuckDuckGo search
        logger.info(f"Character not in repository, searching DuckDuckGo")
        url = self.searcher.search(query)
        
        return url
    
    def add_character(self, name: str, archive_id: str) -> None:
        """
        Add a new character to the repository.
        
        Args:
            name: Character name
            archive_id: Game8 archive ID
        """
        self.character_repo.add(name, archive_id)
        self.character_repo.save()
        logger.info(f"Added character to repository: {name}")
    
    def get_character_count(self) -> int:
        """
        Get total number of characters in repository.
        
        Returns:
            Number of characters
        """
        return self.character_repo.count()
    
    def cleanup(self) -> None:
        """Clean up resources."""
        if self._owns_client and self.http_client:
            self.http_client.close()
            logger.debug("ScraperService cleaned up")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()
