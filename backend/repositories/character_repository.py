"""
Repository pattern implementation for data access.
Abstracts data source and provides clean interface for querying.
"""
import json
from pathlib import Path
from typing import Optional, Dict, List
from difflib import SequenceMatcher

from config.settings import settings
from models import Character
from utils import get_logger


logger = get_logger(__name__)


class CharacterRepository:
    """
    Repository for character data access.
    Handles loading, searching, and managing character information.
    """
    
    def __init__(self, data_file: Optional[Path] = None):
        """
        Initialize repository with character data.
        
        Args:
            data_file: Path to character JSON file (uses settings default if None)
        """
        self.data_file = data_file or settings.CHARACTER_DATA_FILE
        self._characters: Dict[str, Character] = {}
        self._load_data()
    
    def _load_data(self) -> None:
        """Load character data from JSON file."""
        try:
            if not self.data_file.exists():
                logger.warning(f"Character data file not found: {self.data_file}")
                self._characters = {}
                return
            
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            characters_dict = data.get('characters', {})
            self._characters = {
                name: Character(name=name, archive_id=archive_id)
                for name, archive_id in characters_dict.items()
            }
            
            logger.info(f"Loaded {len(self._characters)} characters from {self.data_file}")
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse character data: {e}")
            self._characters = {}
        except Exception as e:
            logger.error(f"Failed to load character data: {e}")
            self._characters = {}
    
    def find_by_name(self, name: str) -> Optional[Character]:
        """
        Find character by exact name match (case-insensitive).
        
        Args:
            name: Character name to search for
        
        Returns:
            Character object if found, None otherwise
        """
        if not name:
            return None
        
        name_lower = name.lower().strip()
        
        for char_name, character in self._characters.items():
            if char_name.lower() == name_lower:
                logger.debug(f"Found exact match: '{name}' -> '{char_name}'")
                return character
        
        return None
    
    def search(self, query: str, threshold: float = 0.6) -> Optional[Character]:
        """
        Search for character using fuzzy matching and substring search.
        
        Args:
            query: Search query string
            threshold: Minimum similarity score (0.0 to 1.0)
        
        Returns:
            Best matching character if found above threshold, None otherwise
        """
        if not query:
            return None
        
        query_lower = query.lower().strip()
        
        # First try exact substring match
        for char_name, character in self._characters.items():
            char_name_lower = char_name.lower()
            
            # Check bidirectional substring match
            if query_lower in char_name_lower or char_name_lower in query_lower:
                logger.info(f"Found substring match: '{query}' matches '{char_name}'")
                return character
        
        # Fuzzy matching as fallback
        best_match = None
        best_score = threshold
        
        for char_name, character in self._characters.items():
            # Calculate similarity ratio
            ratio = SequenceMatcher(None, query_lower, char_name.lower()).ratio()
            
            if ratio > best_score:
                best_score = ratio
                best_match = character
        
        if best_match:
            logger.info(f"Found fuzzy match: '{query}' matches '{best_match.name}' (score: {best_score:.2f})")
        else:
            logger.warning(f"No match found for query: '{query}'")
        
        return best_match
    
    def get_all(self) -> List[Character]:
        """
        Get all characters.
        
        Returns:
            List of all character objects
        """
        return list(self._characters.values())
    
    def add(self, name: str, archive_id: str) -> Character:
        """
        Add a new character to the repository.
        
        Args:
            name: Character name
            archive_id: Game8 archive ID
        
        Returns:
            Newly created character object
        """
        character = Character(name=name, archive_id=archive_id)
        self._characters[name] = character
        logger.info(f"Added character: {name} ({archive_id})")
        return character
    
    def save(self) -> None:
        """Save current character data back to JSON file."""
        try:
            data = {
                'characters': {
                    char.name: char.archive_id
                    for char in self._characters.values()
                }
            }
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(self._characters)} characters to {self.data_file}")
        
        except Exception as e:
            logger.error(f"Failed to save character data: {e}")
            raise
    
    def count(self) -> int:
        """
        Get total number of characters.
        
        Returns:
            Number of characters in repository
        """
        return len(self._characters)
