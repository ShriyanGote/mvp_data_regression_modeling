import requests
from bs4 import BeautifulSoup

def fetch_team_stats(year):
    url_team = f"https://www.basketball-reference.com/leagues/NBA_{year}_standings.html"
    response = requests.get(url_team)
    response.encoding = 'utf-8'

    soup = BeautifulSoup(response.text, 'html.parser')
    eastern_table = soup.find('table', {'id': 'divs_standings_E'})
    western_table = soup.find('table', {'id': 'divs_standings_W'})
    eastern_teams = [extract_team_info(row) for row in eastern_table.find_all('tr', {'class': 'full_table'})]
    western_teams = [extract_team_info(row) for row in western_table.find_all('tr', {'class': 'full_table'})]
    all_teams = bubble_sort(eastern_teams + western_teams)
    
    for i in range(len(all_teams)):
        all_teams[i]['Rank'] = i + 1
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