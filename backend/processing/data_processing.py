import requests
import pandas as pd
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.processing.team_stats import get_team_stats_by_year

# API setup
URL = "https://www.nbaapi.com/graphql/"
HEADERS = {"Content-Type": "application/json"}


def fetch_data(query):
    response = requests.post(URL, headers=HEADERS, json={"query": query, "variables": {}})
    return response.json() if response.status_code == 200 else None


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
    data = fetch_data(query)
    return [{**record, 'season': season} for record in data['data']['playerAdvanced']] if data and 'data' in data and 'playerAdvanced' in data['data'] else []


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
    data = fetch_data(query)
    return [{**record, 'season': season} for record in data['data']['playerTotals']] if data and 'data' in data and 'playerTotals' in data['data'] else []


def fetch_all_seasons_data(first_season=1998, last_season=2024):
    seasons = range(first_season, last_season)
    advanced_stats, totals_stats = [], []
    
    for season in seasons:
        print(f"Fetching advanced data for season {season}...")
        advanced_stats.extend(fetch_player_advanced_data(season))
        print(f"Fetching totals data for season {season}...")
        totals_stats.extend(fetch_player_totals_data(season))
    
    return pd.DataFrame(advanced_stats), pd.DataFrame(totals_stats)


def process_player_data(advanced_df, totals_df):
    if advanced_df.empty or totals_df.empty:
        print("One or both player DataFrames (advanced/totals) are empty. Cannot proceed.")
        return None

    print("Merging advanced and total player data...")
    player_stats = pd.merge(totals_df, advanced_df, on=["playerName", "team", "season"], how="inner")
    player_stats = player_stats[player_stats['team'] != "TOT"]

    player_stats['PPG'] = round(player_stats['points'] / player_stats['games_x'], 2)
    player_stats['APG'] = round(player_stats['assists'] / player_stats['games_x'], 2)
    player_stats['RPG'] = round(player_stats['totalRb'] / player_stats['games_x'], 2)
    player_stats['SPG'] = round(player_stats['steals'] / player_stats['games_x'], 2)
    player_stats['BPG'] = round(player_stats['blocks'] / player_stats['games_x'], 2)
    player_stats['MVP'] = 0  # Placeholder
    
    filtered_players = player_stats[(player_stats['PPG'] > 5) & (player_stats['games_x'] > 50)].copy()
    filtered_players['team'] = filtered_players['team'].str.strip()
    
    return filtered_players


def fetch_and_merge_team_stats(filtered_players, seasons):
    print("Fetching team stats by year...")
    team_stats_by_year = {season: get_team_stats_by_year(season) for season in seasons}
    team_stats_df = pd.concat([pd.DataFrame(stats).assign(season=year) for year, stats in team_stats_by_year.items()])

    team_stats_df.rename(columns={
        'Team Name': 'full_team_name',
        'Team Abbreviation': 'team',
        'Wins': 'wins',
        'Win-Loss Percentage': 'win_percentage',
        'Rank': 'ranking'
    }, inplace=True)

    team_stats_df['team'] = team_stats_df['team'].str.strip()
    team_stats_df['win_percentage'] = team_stats_df['win_percentage'].astype(float)
    
    return pd.merge(
        filtered_players,
        team_stats_df[['season', 'team', 'full_team_name', 'ranking', 'wins', 'win_percentage']],
        on=['season', 'team'],
        how='left'
    )


def compute_player_scores(player_stats, averages_file="data/league_avgs.csv"):
    averages = pd.read_csv(averages_file)
    stat_mapping = {
        "PPG": "Top 20 PPG Avg", "APG": "Top 20 APG Avg", "RPG": "Top 20 RPG Avg",
        "SPG": "Top 20 SPG Avg", "BPG": "Top 20 BPG Avg", "eFG%": "Top 20 eFG% Avg"
    }
    
    for stat, avg_stat in stat_mapping.items():
        averages_dict = averages.set_index("Season")[avg_stat].to_dict()
        player_stats[f"{stat}_Score"] = player_stats.apply(
            lambda row: round(row[stat] / averages_dict[row["season"]], 2)
            if row["season"] in averages_dict and not pd.isna(row[stat]) else None,
            axis=1
        )
    return player_stats

