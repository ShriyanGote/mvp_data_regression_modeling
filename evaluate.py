import requests
import pandas as pd
from calculations.team_stats import get_team_stats_by_year

# API setup
url = "https://www.nbaapi.com/graphql/"
headers = {
    "Content-Type": "application/json"
}


# Function to fetch player advanced stats for a specific season
def fetch_player_advanced_data(season):
    query = f"""
    query PlayerAdvanced {{
        playerAdvanced(season: {season}) {{
            playerName
            position
            team
            games
            per
            usagePercent
            offensiveWs
            defensiveWs
            winShares
            offensiveBox
            defensiveBox
            vorp
        }}
    }}
    """
    payload = {"query": query, "variables": {}}
    response = requests.post(url, headers={"Content-Type": "application/json"}, json=payload)
    if response.status_code == 200:
        data = response.json()
        if 'data' in data and 'playerAdvanced' in data['data']:
            for record in data['data']['playerAdvanced']:
                record['season'] = season
            return data['data']['playerAdvanced']
    return []

# Function to fetch player totals stats for a specific season
def fetch_player_totals_data(season):
    query = f"""
    query PlayerTotals {{
        playerTotals(season: {season}) {{
            playerName
            position
            team
            games
            points
            assists
            totalRb
            steals
            blocks
            turnovers
            effectFgPercent
        }}
    }}
    """
    payload = {"query": query, "variables": {}}
    response = requests.post(url, headers={"Content-Type": "application/json"}, json=payload)
    if response.status_code == 200:
        data = response.json()
        if 'data' in data and 'playerTotals' in data['data']:
            for record in data['data']['playerTotals']:
                record['season'] = season
            return data['data']['playerTotals']
    return []

# Fetch data for multiple seasons
first_season, last_season = 1998, 2024  # Specify the range of seasons
seasons = range(first_season, last_season)  # Include the last season
advanced_stats, totals_stats = [], []

for season in seasons:
    print(f"Fetching advanced data for season {season}...")
    advanced_stats.extend(fetch_player_advanced_data(season))
    print(f"Fetching totals data for season {season}...")
    totals_stats.extend(fetch_player_totals_data(season))

# Convert player data to DataFrames
advanced_df = pd.DataFrame(advanced_stats)
totals_df = pd.DataFrame(totals_stats)

if not advanced_df.empty and not totals_df.empty:
    # Merge advanced and totals data
    print("Merging advanced and totals player data...")
    player_stats = pd.merge(totals_df, advanced_df, on=["playerName", "team", "season"], how="inner")

    # Exclude players who played for multiple teams
    player_stats = player_stats[player_stats['team'] != "TOT"]

    # Calculate additional stats
    player_stats['PPG'] = player_stats['points'] / player_stats['games_x']
    player_stats['APG'] = player_stats['assists'] / player_stats['games_x']
    player_stats['RPG'] = player_stats['totalRb'] / player_stats['games_x']
    player_stats['SPG'] = player_stats['steals'] / player_stats['games_x']
    player_stats['BPG'] = player_stats['blocks'] / player_stats['games_x']
    player_stats['MVP'] = 0
    

    # Filter players
    filtered_players = player_stats[(player_stats['PPG'] > 15) & (player_stats['games_x'] > 50)].copy()
    filtered_players['team'] = filtered_players['team'].str.strip()

    # Fetch and merge team stats by year
    print("Fetching team stats by year...")
    team_stats_by_year = {season: get_team_stats_by_year(season) for season in seasons}
    team_stats_df = pd.concat([pd.DataFrame(stats).assign(season=year) for year, stats in team_stats_by_year.items()])

    # Clean column names
    team_stats_df.rename(columns={
        'Team Name': 'full_team_name',
        'Team Abbreviation': 'team',
        'Wins': 'wins',
        'Win-Loss Percentage': 'win_percentage',
        'Rank': 'ranking'
    }, inplace=True)
    team_stats_df['team'] = team_stats_df['team'].str.strip()
    team_stats_df['win_percentage'] = team_stats_df['win_percentage'].astype(float)

    # Merge the filtered players with team stats
    filtered_players = pd.merge(
        filtered_players,
        team_stats_df[['season', 'team', 'full_team_name', 'ranking', 'wins', 'win_percentage']],
        on=['season', 'team'],
        how='left'
    )
    filtered_players['playerName'] = filtered_players['playerName'].str.replace('*', '', regex=False).str.strip()


    # Save the final dataset
    filtered_players.to_csv("nba_player_stats.csv", index=False)
    print("Final dataset saved to 'nba_player_stats.csv'")
else:
    print("One or both player DataFrames (advanced/totals) are empty. Cannot proceed.")
