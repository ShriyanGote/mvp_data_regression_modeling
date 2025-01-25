import requests

def get_top_scorers(season):
    url = f"https://nba-stats-db.herokuapp.com/api/playerdata/topscorers/total/season/{season}/"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes (e.g., 404, 500)
        data = response.json()

        # Example: Print the top players
        for player in data.get("results", []):
            print(f"Name: {player['player_name']}, Points: {player.get('points', 'N/A')}, Age: {player['age']}, Games Played: {player['games']}")

        return data  # Return the raw data if needed for further processing

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

# Example usage:
season = 2011
top_scorers = get_top_scorers(season)
print(top_scorers)  # Optional: Print the raw data for further processing