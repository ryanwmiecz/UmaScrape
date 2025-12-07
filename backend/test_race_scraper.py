import requests
from bs4 import BeautifulSoup

url = "https://game8.co/games/Umamusume-Pretty-Derby/archives/536131"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

print("Fetching race page...")
response = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(response.content, 'html5lib')

tables = soup.find_all('table', class_='a-table')
main_table = tables[2]
rows = main_table.find_all('tr')

# Test the formatting on Mainichi Okan
for row in rows[1:]:
    cells = row.find_all(['td', 'th'])
    if cells and len(cells) >= 4:
        race_text = cells[2].get_text(strip=True)
        race_name = race_text.split('Racecourse:')[0].strip()
        
        if 'mainichi okan' in race_name.lower():
            period = cells[0].get_text(strip=True)
            
            # Format period with spaces
            formatted_period = ''
            for i, char in enumerate(period):
                if i > 0 and char.isupper() and period[i-1].islower():
                    formatted_period += ' • '
                formatted_period += char
            
            print(f"Race: {race_name}")
            print(f"Original period: {period}")
            print(f"Formatted period: {formatted_period}")
            print(f"Tier: {cells[1].get_text(strip=True)}")
            print(f"Distance: {cells[3].get_text(strip=True)}")
            break

