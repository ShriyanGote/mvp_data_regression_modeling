from nba_api.stats.static import teams
from nba_api.stats.endpoints import commonteamroster, playergamelog
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import os
import json
import time

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def get_active_players(season):
    """Fetch active players for a given season."""
    active_players = []
    nba_teams = teams.get_teams()
    
    for team in nba_teams:
        try:
            roster = commonteamroster.CommonTeamRoster(team_id=team['id'], season=season)
            roster_df = roster.get_data_frames()[0]
            active_players.extend(roster_df[['PLAYER_ID', 'PLAYER']].to_dict('records'))
        except Exception as e:
            print(f"Error fetching roster for {team['full_name']}: {e}")
    
    return active_players

def fetch_game_log(player, season):
    """Fetch game log for a player and calculate average PPG."""
    try:
        game_log = playergamelog.PlayerGameLog(player_id=player['PLAYER_ID'], season=season)
        game_log_df = game_log.get_data_frames()[0]
        avg_ppg = game_log_df['PTS'].mean()
        return {'Player Name': player['PLAYER'], 'PPG': avg_ppg}
    except Exception as e:
        print(f"Error fetching data for {player['PLAYER']}: {e}")
        return None

def fetch_cached_or_live(player, season):
    """Fetch game log data from cache if available, otherwise fetch live data."""
    cache_file = os.path.join(CACHE_DIR, f"{player['PLAYER_ID']}.json")
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            return json.load(f)
    
    result = fetch_game_log(player, season)
    if result:
        with open(cache_file, 'w') as f:
            json.dump(result, f)
    return result

def fetch_all_players_data(season, max_workers=10):
    """Fetch game log data for all active players using parallel execution."""
    active_players = get_active_players(season)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(lambda player: fetch_cached_or_live(player, season), active_players))
    return [result for result in results if result]

def analyze_top_players(player_data, top_n=10):
    """Analyze and return the top N players based on PPG."""
    player_data_df = pd.DataFrame(player_data)
    return player_data_df.sort_values(by='PPG', ascending=False).head(top_n)