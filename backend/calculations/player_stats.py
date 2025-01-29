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
        try:
            mvp = get_mvps(year)
        except KeyError as e:
            print(f"Warning: {e}")
            mvp = None

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

def calculate_score(player_stats):
    try:
        efg = float(player_stats[10]) * 60  # Adjust to float for better compatibility
        stl = float(player_stats[11]) * 20
        rbs = float(player_stats[12]) * 3
        ast = float(player_stats[13]) * 4
        pts = float(player_stats[14]) * 1
        wins = int(player_stats[14])  # Ensure this field is numeric
        rank = int(player_stats[15])  # Ensure this field is numeric

        score = (
            0.15 * (wins + rank)
            + 0.28 * pts
            + 0.12 * rbs
            + 0.16 * ast
            + 0.21 * efg
            + 0.08 * stl
        )
        return round(score, 2)

    except (ValueError, TypeError, IndexError) as e:
        # Log any issues for debugging purposes
        print(f"Error processing player stats: {e}")
        print(f"Problematic player stats: {player_stats}")
        return None
