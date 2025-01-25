import pandas as pd
from calculations.team_stats import fetch_team_stats, get_team
from calculations.player_stats import get_filtered_player_data, get_mvp_data

def prepare_clean_multi_year(start_year, end_year, lwr_points=15, lwr_gs=50, lwr_efg=0.4):
    all_rows = []

    for year in range(start_year, end_year + 1):
        # Fetch data for the year
        try:
            all_teams = fetch_team_stats(year)
            filtered_player_data, mvp = get_filtered_player_data(year, lwr_points, lwr_gs, lwr_efg)
            
            # Parse data for each player
            for name in filtered_player_data['Player']:
                player = get_mvp_data(filtered_player_data, name)
                if player is None:
                    continue

                player_team = get_team(all_teams, str(player[2]))
                if not player_team:
                    continue

                # Add player and team data into a row
                all_rows.append({
                    'Year': year,
                    'Player': name,
                    'PTS': player[28],
                    'AST': player[23],
                    'TRB': player[22],
                    'eFG%': player[16],
                    'Wins': player_team['Wins'],
                    'Rank': player_team['Rank'],
                    'MVP': 1 if mvp and name == mvp else 0  # Handle missing MVP
                })
        except Exception as e:
            print(f"Error processing year {year}: {e}")

    # Create a DataFrame
    data = pd.DataFrame(all_rows)

    # Balance the dataset: Ensure equal or near-equal MVPs and non-MVPs
    mvps = data[data['MVP'] == 1]
    non_mvps = data[data['MVP'] == 0]

    # Sample non-MVPs to match the number of MVPs * x times
    non_mvps_sampled = non_mvps.sample(n=len(mvps) * 5, random_state=42, replace=True)

    # Combine and shuffle the balanced dataset
    balanced_data = pd.concat([mvps, non_mvps_sampled]).sample(frac=1, random_state=42).reset_index(drop=True)

    return balanced_data
