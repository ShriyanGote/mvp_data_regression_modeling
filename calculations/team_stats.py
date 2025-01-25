import requests
from bs4 import BeautifulSoup
import time
import os
import json

# Set up a requests session with headers
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
})

# Ensure the cache directory exists
CACHE_DIR = "cache"
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

def get_team_stats_by_year(year):
    cache_file = os.path.join(CACHE_DIR, f"cache_{year}.json")  # Use cache directory
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as file:
            return json.load(file)
    
    url_team = f"https://www.basketball-reference.com/leagues/NBA_{year}_standings.html"
    response = session.get(url_team)
    
    if response.status_code == 429:
        print("Rate limit reached. Retrying after delay...")
        time.sleep(10)
        response = session.get(url_team)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch data for year {year}: {response.status_code}")
    
    response.encoding = 'utf-8' 
    soup = BeautifulSoup(response.text, 'html.parser')

    eastern_table = soup.find('table', {'id': 'divs_standings_E'})
    western_table = soup.find('table', {'id': 'divs_standings_W'})

    if eastern_table is None or western_table is None:
        raise Exception(f"Could not find standings table for year {year}")

    eastern_teams = [extract_team_info(row) for row in eastern_table.find_all('tr', {'class': 'full_table'})]
    western_teams = [extract_team_info(row) for row in western_table.find_all('tr', {'class': 'full_table'})]
    all_teams = bubble_sort(eastern_teams + western_teams)

    for i in range(len(all_teams)):
        all_teams[i]['Rank'] = len(all_teams) - i - 1  # Adjusted rank calculation
    
    # Save to cache
    with open(cache_file, 'w') as file:
        json.dump(all_teams, file)
    
    return all_teams

def extract_team_info(row):
    try:
        team_name = row.find('a').text
        team_abbr = row.find('a')['href'].split('/')[-2].upper()
        wins = int(row.find('td', {'data-stat': 'wins'}).text)
        losses = int(row.find('td', {'data-stat': 'losses'}).text)
        win_loss_pct = row.find('td', {'data-stat': 'win_loss_pct'}).text
        return {
            'Team Name': team_name,
            'Team Abbreviation': team_abbr,
            'Wins': wins,
            'Losses': losses,
            'Win-Loss Percentage': win_loss_pct
        }
    except Exception as e:
        print(f"Error extracting team info: {e}")
        return None

def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j]['Wins'] > arr[j+1]['Wins']:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

def get_team(all_teams, team_abb):
    for team in all_teams:
        if team['Team Abbreviation'] == team_abb:
            return team
    return None
