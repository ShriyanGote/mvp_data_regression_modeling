from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import commonteamroster, playergamelog
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import os
import json
import time

desired_season = "2022-23"
cache_dir = "cache"
os.makedirs(cache_dir, exist_ok=True)

# Step 1: Fetch active players
def get_active_players(season):
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

# Step 2: Fetch game logs with caching
def fetch_game_log(player):
    try:
        game_log = playergamelog.PlayerGameLog(player_id=player['PLAYER_ID'], season=desired_season)
        game_log_df = game_log.get_data_frames()[0]
        avg_ppg = game_log_df['PTS'].mean()

        return {'Player Name': player['PLAYER'], 'PPG': avg_ppg}
    except Exception as e:
        print(f"Error fetching data for {player['PLAYER']}: {e}")
        return None

def fetch_cached_or_live(player):
    cache_file = os.path.join(cache_dir, f"{player['PLAYER_ID']}.json")
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            return json.load(f)
    result = fetch_game_log(player)
    if result:
        with open(cache_file, 'w') as f:
            json.dump(result, f)
    return result

# Step 3: Use ThreadPoolExecutor for parallelization
active_players = get_active_players(desired_season)
with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(fetch_cached_or_live, active_players))

# Step 4: Filter and analyze data
player_data = [result for result in results if result]
player_data_df = pd.DataFrame(player_data)
top_10_players_df = player_data_df.sort_values(by='PPG', ascending=False).head(10)

# Display results
print(top_10_players_df)
