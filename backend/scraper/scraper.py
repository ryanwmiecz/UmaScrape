import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, unquote, urlparse, parse_qs

# Character URL dictionary - add more as needed
CHARACTER_URLS = {
    #3 Stars
    'Tokai Teio (Peak Joy)': '536320',
    'Tokai Teio (Beyond the Horizon)':'537150',
    'Special Week (Special Dreamer)': '536322',
    'Special Week (Hopp\'n♪Happy Heart)':'556853',
    'Meisho Doto (Turbulent Blue)': '557789',
    'Silence Suzuka (Innocent Silence)': '536321',
    'Mejiro McQueen (End of the Skies)': '537151',
    'Gold City (Authentic / 1928) ':'555980',
    'Oguri Cap (Starlight Beat)': '536318',
    'Maruzensky (Formula R)': '536319',
    'Maruzensky (Hot☆Summer Night)': '556411',
    'Grass Wonder (Saintly Jade Cleric)': '547831',
    'El Condor Pasa (Kukulkan Warrior)': '547832',
    'Taiki Shuttle (Wild Frontier)': '536317',
    'Rice Shower (Rosy Dreams)': '536313',
    'Rice Shower (Vampire Makeover!)':'567547',
    'Super Creek (Chiffon-Wrapped Mummy)':'567548',
    'Biwa Hayahide (pf. Winning Equation...)': '536325',
    'Narita Brian (Maverick)': '541252',
    'Narita Taishin (Nevertheless)':'541215',
    'T.M. Opera O (O Sole Suo!)': '536315',
    'Mayano Top Gun (Sunlight Bouquet)': '541251',
    'Mihono Bourbon (MB-19890425)': '536312',
    'Symboli Rudolf (Emperor\'s Path)': '536314',
    'Hishi Akebono (Buono☆Alla Moda)': '564091',
    'Seiun Sky (Reeling in the Big One)': '547834',
    'Curren Chan (Fille Éclair)': '537177',
    'Mejiro McQueen (Frontline Elegance)': '536316',
    'Kawakami Princess (Princess of Pink)':'568906',
    'Hishi Amazon (Azure Amazon)': '547833',
    'Fuji Kiseki (Shooting Star Revue)': '553122',
    'Smart Falcon (LOVE☆4EVER)': '541253',
    'Air Groove (Quercus Civilis)': '541250',
    'Eishin Flash (Meisterschaft)': '558104',
    'Matikane Fukukitaru (Lucky Tidings)': '562609',
    'Agnes Digital (Full-Color Fangirling)': '566109',
    #2stars
    'Super Creek (Murmuring Stream)' :'536309',
    'Mayano Top Gun (Scramble Zone)' :'536307',
    'Air Groove (Empress Road)':'536302',
    'El Condor Pasa (El Numero 1)': '536304',
    'Grass Wonder (Stone-Piercing Blue)' : '536306',
    'Daiwa Scarlet (Peak Blue)' : '536303',
    'Vodka (Wild Top Gear)' : '536310',
    'Gold Ship (Red Strife)' : '536305',
    #1stars
    'King Halo (King of Emeralds)' : '536295',
    'Nice Nature (Poinsettia Ribbon)' : '536287',
    'Matikane Fukukitaru (Rising Fortune)' : '536296',
    'Haru Urara (Bestest Prize)' : '536294',
    'Sakura Bakushin O (Blossom in Learning)' : '536298',
    'Winning Ticket (Get to Winning!)' : '536299',
    'Agnes Tachyon (Tach-nology)' : '536293',
    'Mejiro Ryan (Down the Line)' : '536297'




}

def find_character_url(search_query):
    """
    Try to find character in dictionary using substring matching
    
    Args:
        search_query: Character name to search for
    Returns:
        str or None: Full URL if found, None otherwise
    """
    if not search_query:
        return None
    
    search_lower = search_query.lower().strip()
    
    # Check if search query is a substring of any character name (case-insensitive)
    for char_name, archive_id in CHARACTER_URLS.items():
        char_name_lower = char_name.lower()
        
        # Check for substring match in either direction
        if search_lower in char_name_lower or char_name_lower in search_lower:
            print(f"Found match: '{search_query}' matches '{char_name}'")
            return f"https://game8.co/games/Umamusume-Pretty-Derby/archives/{archive_id}"
    
    return None

def get_first_search_result(search_query):
    """
    Search DuckDuckGo and return the first result URL
    
    Args:
        search_query: What to search for
    Returns:
        str: URL of first search result
    """
    try:
        # Encode search query for URL
        encoded_query = quote_plus(search_query)
        search_url = f"https://html.duckduckgo.com/html/?q={encoded_query}+build+guide+game8"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0'
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html5lib')
        
        # Try multiple selectors for DuckDuckGo results
        result = None
        
        # Method 1: result__a class
        result = soup.find('a', class_='result__a')
        
        # Method 2: Try finding any link with game8.co in href
        if not result:
            all_links = soup.find_all('a', href=True)
            for link in all_links:
                href = link['href']
                if 'game8.co' in href and 'Umamusume' in href:
                    result = link
                    break
        
        if result and result.get('href'):
            url = result['href']
            # Fix relative URLs (add https: if missing)
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
        
        # No results found
        raise Exception(f"No game8 page found for '{search_query}'. Try a different character name or variation.")
        
    except Exception as e:
        raise Exception(f"Search failed: {str(e)}")

def scrape_data(search_query=None):
    """
    Main scraping function - tries dictionary first, then search
    
    Args:
        search_query: Optional search term. If None, uses default URL
    
    Returns:
        dict: Scraped data in a structured format
    """
    # Try dictionary lookup first
    if search_query:
        url = find_character_url(search_query)
        
        # If not in dictionary, try DuckDuckGo search
        if not url:
            print(f"'{search_query}' not in dictionary, trying search...")
            url = get_first_search_result(search_query)
    else:
        # Default URL if no search query
        url = "https://game8.co/games/Umamusume-Pretty-Derby/archives/536317"
    
    try:
        # Add headers to mimic a browser request
        request_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=request_headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML (using html5lib parser - no C++ compiler needed)
        soup = BeautifulSoup(response.content, 'html5lib')
        
        # Find the header containing "Hidden Events"
        header = soup.find(lambda tag: tag.name in ['h2']
                          and 'Hidden Events' in tag.text)
        
        if not header:
            return {
                'url': url,
                'title': 'No title found',
                'content': []
            }
        
        # Collect all tables after the header until next h2
        tables_data = []
        current = header.find_next_sibling()
        
        while current:
            # Stop if we hit another h2
            if current.name == 'h2':
                break
            # Parse tables into structured data
            if current.name == 'table':
                table_data = parse_table(current)
                if table_data:
                    tables_data.append(table_data)
            # Move to next sibling
            current = current.find_next_sibling()
        
        # Extract data
        data = {
            'url': url,
            'title': header.text.strip(),
            'events': tables_data if tables_data else []
        }
        
        return data
        
    except requests.RequestException as e:
        raise Exception(f"Failed to fetch data: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to parse data: {str(e)}")

def parse_table(table):
    """
    Parse HTML table into clean event data
    
    Args:
        table: BeautifulSoup table element
    Returns:
        dict: Event data with name, conditions, and effects
    """
    # Look for event name (usually in a header above or in first bold text)
    event_name = "Unknown Event"
    
    # Try to find event name from preceding h3 or h4
    prev_header = table.find_previous(['h3', 'h4', 'h5'])
    if prev_header:
        event_name = prev_header.get_text(strip=True)
    
    # Find the data rows (skip header row)
    data_rows = table.find_all('tr')[1:]  # Skip first row (headers)
    
    events = []
    for tr in data_rows:
        cells = tr.find_all(['td', 'th'])
        if len(cells) >= 2:
            # First cell is conditions, second is effects
            conditions = cells[0].get_text(strip=True)
            effects = cells[1].get_text(strip=True)
            
            # Extract event name from conditions if it starts with bold text
            bold = cells[0].find(['b', 'strong'])
            if bold:
                event_name = bold.get_text(strip=True)
                # Remove event name from conditions
                conditions = conditions.replace(event_name, '', 1).strip()
            
            events.append({
                'event_name': event_name,
                'conditions': conditions,
                'effects': effects
            })
    
    return events
