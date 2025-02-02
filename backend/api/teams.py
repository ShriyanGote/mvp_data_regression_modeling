import requests

def fetch_team_data(team_abbr: str, season: str) -> dict:
    """Fetch team data from NBA API (from build.py)"""
    url = "https://www.nbaapi.com/graphql/"
    headers = {"Content-Type": "application/json"}
    
    query = """
    query TEAM($teamAbbr: String!, $season: Int!) {
      team(teamAbbr: $teamAbbr, season: $season, ordering: "-ws") {
        season
        teamName
        coaches
        topWs
        wins
        playoffs
      }
    }
    """
    
    payload = {
        "query": query,
        "variables": {"teamAbbr": team_abbr, "season": season}
    }
    
    response = requests.post(url, headers=headers, json=payload)
    return response.json() if response.status_code == 200 else None