"""
Race matching service for finding races mentioned in character events.
"""
from typing import Dict, List, Set, Optional
from bs4 import BeautifulSoup
import re

from config.settings import settings
from models import Race, RaceMatch
from utils import HTTPClient, get_logger


logger = get_logger(__name__)


class RaceMatcher:
    """Service for matching races mentioned in events."""
    
    def __init__(self, http_client: Optional[HTTPClient] = None):
        """
        Initialize race matcher.
        
        Args:
            http_client: HTTP client for fetching race data
        """
        self.http_client = http_client or HTTPClient()
        self._owns_client = http_client is None
        self._race_cache: Optional[Dict[str, Race]] = None
    
    def get_race_list(self, force_refresh: bool = False) -> Dict[str, Race]:
        """
        Get dictionary of all races with their details.
        Uses caching to avoid repeated requests.
        
        Args:
            force_refresh: Force refresh of cached data
        
        Returns:
            Dictionary mapping race names to Race objects
        """
        if self._race_cache is not None and not force_refresh:
            logger.debug(f"Using cached race list ({len(self._race_cache)} races)")
            return self._race_cache
        
        try:
            logger.info(f"Fetching race list from {settings.GAME8_RACE_LIST_URL}")
            
            response = self.http_client.get(settings.GAME8_RACE_LIST_URL)
            soup = BeautifulSoup(response.content, 'html5lib')
            
            # Find all tables with class 'a-table'
            tables = soup.find_all('table', class_='a-table')
            
            if len(tables) < 3:
                logger.warning(f"Expected at least 3 tables, found {len(tables)}")
                return {}
            
            # Main race schedule table is table 2 (index 2)
            race_table = tables[2]
            races = self._parse_race_table(race_table)
            
            self._race_cache = races
            logger.info(f"Loaded {len(races)} races into cache")
            
            return races
        
        except Exception as e:
            logger.error(f"Failed to fetch race list: {str(e)}", exc_info=True)
            return {}
    
    def _parse_race_table(self, table) -> Dict[str, Race]:
        """
        Parse race table into Race objects.
        
        Args:
            table: BeautifulSoup table element
        
        Returns:
            Dictionary mapping race names to Race objects
        """
        races = {}
        rows = table.find_all('tr')[1:]  # Skip header
        
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if cells and len(cells) >= 4:
                # Cell 0: Period, Cell 1: Tier, Cell 2: Race name, Cell 3: Distance
                period = cells[0].get_text(strip=True)
                tier = cells[1].get_text(strip=True)
                race_text = cells[2].get_text(strip=True)
                distance = cells[3].get_text(strip=True)
                
                # Format period with bullet separators
                formatted_period = self._format_period(period)
                
                # Extract race name (before "Racecourse:")
                race_name = race_text.split('Racecourse:')[0].strip()
                
                if race_name:
                    races[race_name] = Race(
                        name=race_name,
                        period=formatted_period,
                        tier=tier,
                        distance=distance
                    )
        
        return races
    
    @staticmethod
    def _format_period(period: str) -> str:
        """
        Format period string with bullet separators.
        Example: "EarlyOctClassicSenior" -> "Early Oct • Classic • Senior"
        
        Args:
            period: Raw period string
        
        Returns:
            Formatted period string
        """
        formatted = ''
        for i, char in enumerate(period):
            if i > 0 and char.isupper() and period[i-1].islower():
                formatted += ' • '
            formatted += char
        return formatted
    
    def find_matching_races(
        self,
        events: List,
        race_dict: Optional[Dict[str, Race]] = None
    ) -> List[RaceMatch]:
        """
        Find which races from the race list are mentioned in events.
        
        Args:
            events: List of Event objects or dictionaries
            race_dict: Race dictionary (fetches if None)
        
        Returns:
            List of RaceMatch objects
        """
        if race_dict is None:
            race_dict = self.get_race_list()
        
        if not race_dict:
            logger.warning("No race dictionary available for matching")
            return []
        
        matches = []
        seen_races: Set[str] = set()
        
        # Flatten nested event lists
        flat_events = self._flatten_events(events)
        
        logger.debug(f"Matching {len(flat_events)} events against {len(race_dict)} races")
        
        for event in flat_events:
            # Handle both Event objects and dictionaries
            if hasattr(event, 'event_name'):
                # It's an Event object
                event_name = event.event_name
                conditions = event.conditions
                effects = event.effects
            else:
                # It's a dictionary
                event_name = event.get('event_name', '')
                conditions = event.get('conditions', '')
                effects = event.get('effects', '')
            
            event_text = f"{event_name} {conditions} {effects}".lower()
            
            for race_name, race in race_dict.items():
                race_lower = race_name.lower()
                
                # Check if race name appears in event text
                if race_lower in event_text and race_name not in seen_races:
                    logger.debug(f"Match: '{race_name}' found in event '{event_name}'")
                    
                    mentioned_in = 'conditions' if race_lower in conditions.lower() else 'effects'
                    
                    matches.append(RaceMatch(
                        race=race_name,
                        period=race.period,
                        tier=race.tier,
                        distance=race.distance,
                        event_name=event_name,
                        mentioned_in=mentioned_in
                    ))
                    seen_races.add(race_name)
        
        logger.info(f"Found {len(matches)} race matches")
        return matches
    
    @staticmethod
    def _flatten_events(events: List) -> List:
        """
        Flatten nested event lists.
        
        Args:
            events: Possibly nested list of events
        
        Returns:
            Flattened list of events
        """
        flat_events = []
        for event in events:
            if isinstance(event, list):
                flat_events.extend(event)
            else:
                flat_events.append(event)
        return flat_events
    
    def cleanup(self) -> None:
        """Clean up resources if we own the HTTP client."""
        if self._owns_client and self.http_client:
            self.http_client.close()

