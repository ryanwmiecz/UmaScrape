"""
Strategy pattern implementation for different scraping approaches.
Allows adding new scrapers without modifying existing code (Open/Closed Principle).
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, unquote, urlparse, parse_qs
import re

from config.settings import settings
from models import Event, CharacterData, RecommendedStats
from utils import HTTPClient, get_logger


logger = get_logger(__name__)


class ScraperStrategy(ABC):
    """Abstract base class for scraping strategies."""
    
    def __init__(self, http_client: Optional[HTTPClient] = None):
        """
        Initialize scraper with HTTP client.
        
        Args:
            http_client: HTTP client for making requests (creates new if None)
        """
        self.http_client = http_client or HTTPClient()
        self._owns_client = http_client is None
    
    @abstractmethod
    def scrape(self, url: str) -> CharacterData:
        """
        Scrape data from the given URL.
        
        Args:
            url: URL to scrape
        
        Returns:
            CharacterData object with scraped information
        
        Raises:
            Exception: On scraping failure
        """
        pass
    
    def cleanup(self) -> None:
        """Clean up resources if we own the HTTP client."""
        if self._owns_client and self.http_client:
            self.http_client.close()


class Game8Scraper(ScraperStrategy):
    """Scraper for Game8 Umamusume character pages."""
    
    TIER_LIST_URL = "https://game8.co/games/Umamusume-Pretty-Derby/archives/536352"
    
    def scrape(self, url: str) -> CharacterData:
        """
        Scrape character data from Game8 page.
        
        Args:
            url: Game8 character page URL
        
        Returns:
            CharacterData with events parsed from page
        
        Raises:
            Exception: On fetch or parse failure
        """
        try:
            logger.info(f"Scraping Game8 page: {url}")
            
            response = self.http_client.get(url)
            soup = BeautifulSoup(response.content, 'html5lib')
            
            # Extract character name from the page
            character_name = self._extract_character_name(soup, url)
            
            # Scrape the overall rank from tier list
            overall_rank = self._scrape_overall_rank(character_name)
            
            # Scrape recommended stats
            recommended_stats = self._scrape_recommended_stats(soup)
            
            # Find the "Hidden Events" section
            header = soup.find(
                lambda tag: tag.name == 'h2' and 'Hidden Events' in tag.text
            )
            
            if not header:
                logger.warning(f"No 'Hidden Events' section found on {url}")
                return CharacterData(
                    url=url,
                    title='No title found',
                    events=[],
                    overall_rank=overall_rank,
                    recommended_stats=recommended_stats
                )
            
            title = header.text.strip()
            logger.debug(f"Found section: {title}")
            
            # Parse all tables in the section
            events = self._parse_events_section(header)
            
            logger.info(f"Successfully scraped {len(events)} events from {url}")
            
            return CharacterData(
                url=url,
                title=title,
                events=events,
                overall_rank=overall_rank,
                recommended_stats=recommended_stats
            )
        
        except Exception as e:
            logger.error(f"Failed to scrape {url}: {str(e)}", exc_info=True)
            raise Exception(f"Failed to scrape Game8 page: {str(e)}") from e
    
    def _parse_events_section(self, header) -> List[Event]:
        """
        Parse all event tables following the header.
        
        Args:
            header: BeautifulSoup element for section header
        
        Returns:
            List of Event objects
        """
        events = []
        current = header.find_next_sibling()
        
        while current:
            # Stop at next h2 section
            if current.name == 'h2':
                break
            
            # Parse tables
            if current.name == 'table':
                table_events = self._parse_event_table(current)
                events.extend(table_events)
            
            current = current.find_next_sibling()
        
        return events
    
    def _parse_event_table(self, table) -> List[Event]:
        """
        Parse a single event table.
        
        Args:
            table: BeautifulSoup table element
        
        Returns:
            List of Event objects from table
        """
        # Try to find event name from preceding header
        event_name = "Unknown Event"
        prev_header = table.find_previous(['h3', 'h4', 'h5'])
        if prev_header:
            event_name = prev_header.get_text(strip=True)
        
        events = []
        rows = table.find_all('tr')[1:]  # Skip header row
        
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 2:
                # Extract conditions and effects
                conditions = cells[0].get_text(separator=' ', strip=True)
                effects_raw = cells[1].get_text(separator=' ', strip=True)
                
                # Format effects with commas
                effects = self._format_effects(effects_raw)
                
                # Extract event name from bold text in conditions if present
                bold = cells[0].find(['b', 'strong'])
                if bold:
                    event_name = bold.get_text(strip=True)
                    conditions = conditions.replace(event_name, '', 1).strip()
                
                events.append(Event(
                    event_name=event_name,
                    conditions=conditions,
                    effects=effects
                ))
        
        return events
    
    @staticmethod
    def _format_effects(effects_raw: str) -> str:
        """
        Format effects string with proper comma separation.
        
        Args:
            effects_raw: Raw effects text
        
        Returns:
            Formatted effects string
        """
        # Add comma before stat names
        effects = re.sub(
            r'(\+\d+)\s+(Speed|Power|Stamina|Guts|Wisdom|Skill Points)',
            r'\1, \2',
            effects_raw
        )
        # Add comma before skill level ups
        effects = re.sub(r'(\+\d+)\s+([A-Z])', r'\1, \2', effects)
        return effects
    
    def _extract_character_name(self, soup: BeautifulSoup, url: str) -> str:
        """
        Extract character name from the page.
        
        Args:
            soup: BeautifulSoup object of the character page
            url: Character page URL
        
        Returns:
            Character name string
        """
        # Try to get from page title
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text()
            # Extract character name from title like "Oguri Cap (Starlight Beat) Build Guide"
            match = re.match(r'^(.*?)\s+Build\s+Guide', title)
            if match:
                return match.group(1).strip()
        
        # Try to get from h1 tag
        h1 = soup.find('h1')
        if h1:
            text = h1.get_text(strip=True)
            match = re.match(r'^(.*?)\s+Build\s+Guide', text)
            if match:
                return match.group(1).strip()
            return text
        
        # Fallback: extract from URL
        logger.warning(f"Could not extract character name from page, using URL")
        return url.split('/')[-1]
    
    def _scrape_recommended_stats(self, soup: BeautifulSoup) -> Optional[RecommendedStats]:
        """
        Scrape recommended stats from the character page.
        
        Args:
            soup: BeautifulSoup object of the character page
        
        Returns:
            RecommendedStats object or None if not found
        """
        try:
            # Find the "Recommended Stats" header
            header = soup.find('h3', id='hm_6')
            if not header or 'Recommended Stats' not in header.get_text():
                logger.debug("Recommended Stats section not found")
                return None
            
            # Find the table after the header
            table = header.find_next('table')
            if not table:
                logger.debug("No table found after Recommended Stats header")
                return None
            
            # Find the tbody
            tbody = table.find('tbody')
            if not tbody:
                logger.debug("No tbody found in stats table")
                return None
            
            rows = tbody.find_all('tr')
            if len(rows) < 2:
                logger.debug("Not enough rows in stats table")
                return None
            
            # First row has the stat icons with alt text
            header_row = rows[0]
            stat_headers = []
            for th in header_row.find_all('th'):
                img = th.find('img', alt=True)
                if img:
                    stat_name = img.get('alt', '').strip().lower()
                    stat_headers.append(stat_name)
            
            # Second row has the values
            value_row = rows[1]
            stat_values = []
            for td in value_row.find_all('td'):
                bold = td.find('b')
                if bold:
                    try:
                        value = int(bold.get_text(strip=True))
                        stat_values.append(value)
                    except ValueError:
                        logger.warning(f"Could not parse stat value: {bold.get_text()}")
                        return None
            
            # Map stats to the expected names
            if len(stat_headers) != 5 or len(stat_values) != 5:
                logger.warning(f"Expected 5 stats, got {len(stat_headers)} headers and {len(stat_values)} values")
                return None
            
            stats_dict = dict(zip(stat_headers, stat_values))
            
            return RecommendedStats(
                speed=stats_dict.get('speed', 0),
                stamina=stats_dict.get('stamina', 0),
                power=stats_dict.get('power', 0),
                guts=stats_dict.get('guts', 0),
                wit=stats_dict.get('wit', 0)
            )
            
        except Exception as e:
            logger.error(f"Failed to scrape recommended stats: {str(e)}", exc_info=True)
            return None
    
    def _scrape_overall_rank(self, character_name: str) -> Optional[str]:
        """
        Scrape the overall rank for a character from the tier list page.
        
        Args:
            character_name: Name of the character to find rank for
        
        Returns:
            Rank string (SS, S, A, or B) or None if not found
        """
        try:
            # Extract base character name (remove variant in parentheses)
            base_name = re.sub(r'\s*\([^)]*\)', '', character_name).strip()
            
            response = self.http_client.get(self.TIER_LIST_URL)
            soup = BeautifulSoup(response.content, 'html5lib')
            
            # Find all tables on the page
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) < 2:
                        continue
                    
                    # First cell contains rank - check image alt attribute
                    rank_cell = cells[0]
                    rank_img = rank_cell.find('img', alt=True)
                    if not rank_img:
                        continue
                    
                    rank_text = rank_img.get('alt', '')
                    
                    # Check if first cell has a rank pattern
                    rank_match = re.search(r'\b(SS|S|A|B)\s+Rank\b', rank_text)
                    if not rank_match:
                        continue
                    
                    rank = rank_match.group(1)
                    
                    # Second cell contains character names - get from image alt attributes
                    characters_cell = cells[1]
                    character_images = characters_cell.find_all('img', alt=True)
                    
                    for img in character_images:
                        img_alt = img.get('alt', '').strip()
                        
                        # Skip rank indicator images
                        if 'Rank' in img_alt and len(img_alt) < 15:
                            continue
                        
                        # Remove variant in parentheses from alt text for comparison
                        img_base = re.sub(r'\s*\([^)]*\)', '', img_alt).strip()
                        
                        # Check if this matches our character
                        if base_name.lower() == img_base.lower():
                            return rank
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to scrape overall rank: {str(e)}", exc_info=True)
            return None


class DuckDuckGoSearcher(ScraperStrategy):
    """Searcher that finds Game8 pages via DuckDuckGo search."""
    
    def scrape(self, url: str) -> CharacterData:
        """
        This strategy doesn't scrape a URL, use search() instead.
        
        Raises:
            NotImplementedError: Always (use search method)
        """
        raise NotImplementedError("Use search() method for DuckDuckGoSearcher")
    
    def search(self, search_query: str) -> str:
        """
        Search DuckDuckGo for character and return first Game8 result URL.
        
        Args:
            search_query: Character name to search for
        
        Returns:
            URL of first Game8 result
        
        Raises:
            Exception: If no results found or search fails
        """
        try:
            logger.info(f"Searching DuckDuckGo for: {search_query}")
            
            # Build search URL
            encoded_query = quote_plus(search_query)
            search_url = f"{settings.DUCKDUCKGO_SEARCH_URL}?q={encoded_query}+build+guide+game8"
            
            response = self.http_client.get(search_url)
            soup = BeautifulSoup(response.content, 'html5lib')
            
            # Try to find Game8 result
            result_url = self._extract_result_url(soup)
            
            if not result_url:
                raise Exception(
                    f"No game8 page found for '{search_query}'. "
                    f"Try a different character name or variation."
                )
            
            logger.info(f"Found Game8 URL: {result_url}")
            return result_url
        
        except Exception as e:
            logger.error(f"Search failed for '{search_query}': {str(e)}")
            raise Exception(f"Search failed: {str(e)}") from e
    
    def _extract_result_url(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extract Game8 URL from DuckDuckGo search results.
        
        Args:
            soup: BeautifulSoup object of search results page
        
        Returns:
            Game8 URL if found, None otherwise
        """
        # Method 1: result__a class
        result = soup.find('a', class_='result__a')
        
        # Method 2: Find any link with game8.co in href
        if not result:
            all_links = soup.find_all('a', href=True)
            for link in all_links:
                href = link['href']
                if 'game8.co' in href and 'Umamusume' in href:
                    result = link
                    break
        
        if not result or not result.get('href'):
            return None
        
        url = result['href']
        
        # Fix relative URLs
        if url.startswith('//'):
            url = 'https:' + url
        
        # Extract actual URL from DuckDuckGo redirect
        if 'duckduckgo.com/l/' in url:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            if 'uddg' in params:
                actual_url = unquote(params['uddg'][0])
                return actual_url
        
        return url
