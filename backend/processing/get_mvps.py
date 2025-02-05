import requests
from bs4 import BeautifulSoup

def get_mvps(given_year):
    my_hash = {}
    url_player = "https://www.basketball-reference.com/awards/mvp.html"
    response_player = requests.get(url_player)
    response_player.encoding = 'utf-8'

    soup = BeautifulSoup(response_player.text, 'html.parser')
    nba_winners = soup.find('table', {'id': 'mvp_NBA'})
    rows = nba_winners.find_all('tr')

    for row in rows[1:]:
        columns = row.find_all('td')
        if len(columns) > 0:
            year_link = columns[0].find('a')['href']
            year = year_link.split('/')[-1].split('_')[1].split('.')[0]
            player = columns[1].text.strip()
            my_hash[year] = player

    # # Debug print
    # print("MVP Hash:", my_hash)

    # Handle missing year
    if str(given_year) not in my_hash:
        raise KeyError(f"MVP data for year {given_year} is not available.")

    return my_hash[str(given_year)]
