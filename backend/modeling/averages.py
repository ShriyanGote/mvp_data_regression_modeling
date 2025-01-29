import pandas as pd

player_stats = pd.read_csv("data/nba_player_stats.csv")
averages = pd.read_csv("data/league_avgs.csv")

if player_stats['season'].dtype != 'object':  # Ensure it's not already in "YYYY-YY" format
    player_stats['season'] = player_stats['season'].apply(lambda x: f"{x}-{str(int(x) + 1)[-2:]}")

missing_seasons = set(player_stats['season']) - set(averages['Season'])
if missing_seasons:
    print(f"Missing these seasons: {missing_seasons}. Proceeding with available seasons.")

stat_mapping = {
    "PPG": "PPG",
    "APG": "APG",
    "RPG": "RPG",
    "SPG": "SPG",
    "BPG": "BPG",
    "eFG%": "effectFgPercent"  
}

# Calculate scores for each stat
for stat, avg_stat in [("PPG", "Top 20 PPG Avg"), ("APG", "Top 20 APG Avg"),
                       ("RPG", "Top 20 RPG Avg"), ("SPG", "Top 20 SPG Avg"),
                       ("BPG", "Top 20 BPG Avg"), ("eFG%", "Top 20 eFG% Avg")]:
    player_stat_column = stat_mapping.get(stat)  # Find the corresponding column in player_stats
    if player_stat_column:
        averages_dict = averages.set_index("Season")[avg_stat].to_dict()
        player_stats[f"{stat}_Score"] = player_stats.apply(
            lambda row: round(row[player_stat_column] / averages_dict[row["season"]], 2)
            if row["season"] in averages_dict and not pd.isna(row[player_stat_column]) else None,
            axis=1
        )

# Save the updated DataFrame with calculated scores
player_stats.to_csv("nba_player_stats_with_scores.csv", index=False)
print("Scores recalculated and saved successfully.")
