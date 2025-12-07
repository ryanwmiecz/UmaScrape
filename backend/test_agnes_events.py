import requests
from bs4 import BeautifulSoup

url = "https://game8.co/games/Umamusume-Pretty-Derby/archives/334848"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

print("Fetching Agnes Tachyon page...")
response = requests.get(url, headers=headers, timeout=5)
soup = BeautifulSoup(response.content, 'html5lib')

# Find Hidden Events section
current_pos = soup.find('h2', string=lambda s: s and 'Hidden Events' in s)

if current_pos:
    print("\nFound Hidden Events section\n")
    
    # Process tables until next h2
    events_found = 0
    for sibling in current_pos.find_next_siblings():
        if sibling.name == 'h2':
            break
        
        if sibling.name == 'table' and 'a-table' in sibling.get('class', []):
            events_found += 1
            print(f"=== EVENT TABLE {events_found} ===")
            
            rows = sibling.find_all('tr')
            for i, row in enumerate(rows):
                cells = row.find_all(['td', 'th'])
                if cells:
                    print(f"\nRow {i}:")
                    for j, cell in enumerate(cells):
                        text = cell.get_text(separator=' ', strip=True)
                        print(f"  Cell {j}: {text[:200]}")
            print()
