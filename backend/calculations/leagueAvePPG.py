from nba_api.stats.endpoints import leaguedashplayerstats
import pandas as pd
import time

# Define the range of seasons
start_season = 1998
end_season = 2023
season_ids = [f"{year}-{str(year + 1)[-2:]}" for year in range(start_season, end_season)]

# Initialize a list to store results for each season
season_stat_analysis = []

# Function to calculate eFG%
def calculate_efg(fgm, fga, fg3m):
    if fga == 0:  # Avoid division by zero
        return 0
    return (fgm + 0.5 * fg3m) / fga

# Function to fetch and process data for a season
def fetch_season_data(season):
    try:
        print(f"Fetching data for season {season}...")
        
        # Fetch player stats for the season
        league_stats = leaguedashplayerstats.LeagueDashPlayerStats(
            season=season, season_type_all_star="Regular Season"
        )
        stats_df = league_stats.get_data_frames()[0]

        # Calculate Points Per Game (PPG), Assists Per Game (APG), etc.
        stats_df['PPG'] = stats_df['PTS'] / stats_df['GP']
        stats_df['APG'] = stats_df['AST'] / stats_df['GP']
        stats_df['RPG'] = stats_df['REB'] / stats_df['GP']
        stats_df['SPG'] = stats_df['STL'] / stats_df['GP']
        stats_df['BPG'] = stats_df['BLK'] / stats_df['GP']
        stats_df['eFG%'] = stats_df.apply(
            lambda row: calculate_efg(row['FGM'], row['FGA'], row['FG3M']), axis=1
        )

        # League-wide averages
        league_averages = {
            'PPG': stats_df['PPG'].mean(),
            'APG': stats_df['APG'].mean(),
            'RPG': stats_df['RPG'].mean(),
            'SPG': stats_df['SPG'].mean(),
            'BPG': stats_df['BPG'].mean(),
            'eFG%': stats_df['eFG%'].mean()
        }

        # Top 20 players by PPG, APG, RPG, SPG, BPG, and eFG%
        top_20_stats = {}
        for stat in ['PPG', 'APG', 'RPG', 'SPG', 'BPG', 'eFG%']:
            top_20 = stats_df.sort_values(by=stat, ascending=False).head(20)
            top_20_stats[f'Top 20 {stat} Avg'] = top_20[stat].mean()

        # Combine results
        season_data = {'Season': season}
        season_data.update({f'League Average {stat}': avg for stat, avg in league_averages.items()})
        season_data.update(top_20_stats)

        return season_data
    except Exception as e:
        print(f"Error processing season {season}: {e}")
        return None

# Process each season
for season in season_ids:
    season_data = fetch_season_data(season)
    if season_data:
        season_stat_analysis.append(season_data)

    # Add a delay to avoid rate limiting
    time.sleep(2)

# Convert the results to a DataFrame
season_stat_df = pd.DataFrame(season_stat_analysis)

# Save to CSV
season_stat_df.to_csv("NBA_league_avgs.csv", index=False)

# Display the results
print(season_stat_df)
