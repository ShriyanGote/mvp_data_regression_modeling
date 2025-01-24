import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from calculations.mvp_calculations import get_mvps

def get_filtered_player_data(year, lwr_points, lwr_gs, lwr_efg):
    try:
        # Fetch data from the basketball reference site
        url_player = f"https://www.basketball-reference.com/leagues/NBA_{year}_per_game.html"
        response_player = requests.get(url_player)
        response_player.encoding = 'utf-8'
        #shriyans

        # Parse the HTML page
        stats_page = BeautifulSoup(response_player.text, 'html.parser')
        column_headers = [header.getText() for header in stats_page.findAll('tr')[0].findAll("th")]
        rows = stats_page.findAll('tr')[1:]
        player_stats = [
            [col.getText() for col in row.findAll("td")]
            for row in rows if row.find("td")
        ]

        # Create a DataFrame
        data = pd.DataFrame(player_stats, columns=column_headers[1:])
        mvp_categories = ["GS", "eFG%", "STL", "TRB", "AST", "PTS"]
        for category in mvp_categories:
            data[category] = pd.to_numeric(data[category], errors='coerce')

        # Filter data
        filtered_data = data[
            (data["PTS"] > lwr_points) &
            (data["GS"] > lwr_gs) &
            (data["eFG%"] > lwr_efg)
        ].copy()

        # Rank players based on categories
        for category in mvp_categories:
            filtered_data[f"{category}_Rk"] = filtered_data[category].rank(pct=True)

        # Get MVP data
        mvp = get_mvps(year)
        return filtered_data, mvp

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Error fetching data for year {year}: {e}")
    except KeyError as e:
        raise RuntimeError(f"Missing expected column in the data: {e}")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred in get_filtered_player_data: {e}")


def get_mvp_data(data, player):
    try:
        # Check if the player exists in the data
        row = data[data['Player'] == player]
        print(row)
        if row.empty:
            return None
        
        # Process the player's data row
        row_array = np.asarray(row)[0]
        numeric_indices = [i for i in range(4, 29)]  # Indices of numeric fields
        row_array = [
            float(row_array[i]) if i in numeric_indices and row_array[i] != '' else 0.0
            if i in numeric_indices else row_array[i]
            for i in range(len(row_array))
        ]

        return row_array

    except KeyError as e:
        raise RuntimeError(f"The data does not contain the expected columns: {e}")
    except IndexError as e:
        raise RuntimeError(f"Error accessing player data for {player}: {e}")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred in get_mvp_data: {e}")


def calculate_score(player_stats, team_stats):
    try:
        # Calculate the MVP score based on player and team statistics
        efg = player_stats[16] * 60
        stl = player_stats[24] * 10
        blk = player_stats[25] * 10
        rbs = player_stats[22] * 3
        ast = player_stats[23] * 3
        pts = player_stats[28]
        rank = team_stats['Rank']
        wins = team_stats['Wins']
        score = (0.10 * (wins + rank)) + (0.28 * pts) + (0.12 * rbs) + (0.16 * ast) + (0.21 * efg) + (0.08 * (stl + blk))
        return round(score, 2)

    except IndexError as e:
        raise RuntimeError(f"Error accessing player statistics: {e}")
    except KeyError as e:
        raise RuntimeError(f"Missing required key in team statistics: {e}")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred in calculate_score: {e}")
