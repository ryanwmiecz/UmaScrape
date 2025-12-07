import requests
from bs4 import BeautifulSoup

def scrape_race_list():
    """
    Scrape the race list from Game8
    
    Returns:
        dict: Dictionary mapping race names to their details (period, tier, distance)
    """
    try:
        url = "https://game8.co/games/Umamusume-Pretty-Derby/archives/536131"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html5lib')
        
        # Find all tables with class 'a-table' - the main race table is table 2 (index 2)
        tables = soup.find_all('table', class_='a-table')
        
        if len(tables) < 3:
            print(f"Expected at least 3 tables, found {len(tables)}")
            return {}
        
        race_table = tables[2]  # Main race schedule table
        
        races = {}
        # Get all tr elements
        rows = race_table.find_all('tr')
        
        for row in rows[1:]:  # Skip header row
            cells = row.find_all(['td', 'th'])
            if cells and len(cells) >= 4:
                # Cell 0: Period, Cell 1: Tier, Cell 2: Race name, Cell 3: Distance
                period = cells[0].get_text(strip=True)
                tier = cells[1].get_text(strip=True)
                race_text = cells[2].get_text(strip=True)
                distance = cells[3].get_text(strip=True)
                
                # Format period with spaces (e.g., "Early OctClassicSenior" -> "Early Oct • Classic • Senior")
                # Insert space before capital letters
                formatted_period = ''
                for i, char in enumerate(period):
                    if i > 0 and char.isupper() and period[i-1].islower():
                        formatted_period += ' • '
                    formatted_period += char
                
                # Extract just the race name before "Racecourse:"
                race_name = race_text.split('Racecourse:')[0].strip()
                if race_name:
                    races[race_name] = {
                        'period': formatted_period,
                        'tier': tier,
                        'distance': distance
                    }
        
        print(f"Found {len(races)} races in database")
        return races
        
    except Exception as e:
        print(f"Failed to scrape race list: {str(e)}")
        return []

def find_matching_races(events, race_dict):
    """
    Find which races from the race list are mentioned in events
    
    Args:
        events: List of event dictionaries with conditions and effects
        race_dict: Dictionary mapping race names to their details
        
    Returns:
        list: List of matching races with event context and race details
    """
    matches = []
    seen_races = set()  # Avoid duplicates
    
    print(f"Checking {len(events)} events against {len(race_dict)} races")
    
    # Flatten events if nested
    flat_events = []
    for event in events:
        if isinstance(event, list):
            flat_events.extend(event)
        else:
            flat_events.append(event)
    
    print(f"Flattened to {len(flat_events)} events")
    
    for event in flat_events:
        event_text = f"{event.get('event_name', '')} {event.get('conditions', '')} {event.get('effects', '')}".lower()
        print(f"Event text: {event_text[:100]}...")  # Debug: show first 100 chars
        
        for race_name, race_details in race_dict.items():
            race_lower = race_name.lower()
            # Check if race name appears in event text
            if race_lower in event_text and race_name not in seen_races:
                print(f"MATCH: Found '{race_name}' in event!")
                matches.append({
                    'race': race_name,
                    'period': race_details['period'],
                    'tier': race_details['tier'],
                    'distance': race_details['distance'],
                    'event_name': event.get('event_name', 'Unknown'),
                    'mentioned_in': 'conditions' if race_lower in event.get('conditions', '').lower() else 'effects'
                })
                seen_races.add(race_name)
    
    print(f"Total matches found: {len(matches)}")
    return matches

