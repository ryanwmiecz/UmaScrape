"""
Data models for scraper application.
Provides type-safe data structures with validation.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class Event:
    """Represents a character event with conditions and effects."""
    
    event_name: str
    conditions: str
    effects: str
    
    def to_dict(self) -> Dict[str, str]:
        """Convert event to dictionary format."""
        return {
            'event_name': self.event_name,
            'conditions': self.conditions,
            'effects': self.effects
        }


@dataclass
class Race:
    """Represents a race with scheduling and difficulty information."""
    
    name: str
    period: str
    tier: str
    distance: str
    
    def to_dict(self) -> Dict[str, str]:
        """Convert race to dictionary format."""
        return {
            'name': self.name,
            'period': self.period,
            'tier': self.tier,
            'distance': self.distance
        }


@dataclass
class RaceMatch:
    """Represents a race mentioned in character events."""
    
    race: str
    period: str
    tier: str
    distance: str
    event_name: str
    mentioned_in: str  # 'conditions' or 'effects'
    
    def to_dict(self) -> Dict[str, str]:
        """Convert race match to dictionary format."""
        return {
            'race': self.race,
            'period': self.period,
            'tier': self.tier,
            'distance': self.distance,
            'event_name': self.event_name,
            'mentioned_in': self.mentioned_in
        }


@dataclass
class CharacterData:
    """Complete character data including events and race information."""
    
    url: str
    title: str
    events: List[Event] = field(default_factory=list)
    matching_races: List[RaceMatch] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert character data to dictionary format for API response."""
        return {
            'url': self.url,
            'title': self.title,
            'events': [event.to_dict() for event in self.events],
            'matching_races': [race.to_dict() for race in self.matching_races]
        }
    
    def add_event(self, event: Event) -> None:
        """Add an event to the character data."""
        self.events.append(event)
    
    def add_race_match(self, race_match: RaceMatch) -> None:
        """Add a race match to the character data."""
        self.matching_races.append(race_match)


@dataclass
class ScraperResult:
    """Result from scraping operation with success status."""
    
    success: bool
    data: Optional[CharacterData] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary format for API response."""
        result = {'success': self.success}
        
        if self.data:
            result['data'] = self.data.to_dict()
            result['url'] = self.data.url
        
        if self.error:
            result['error'] = self.error
        
        return result


@dataclass
class Character:
    """Represents a character with their archive ID."""
    
    name: str
    archive_id: str
    
    @property
    def url(self) -> str:
        """Generate the full Game8 URL for this character."""
        from config.settings import settings
        return f"{settings.GAME8_BASE_URL}/{self.archive_id}"
