import requests

# Define the API URL
url = "https://www.nbaapi.com/graphql/"

# Define the headers
headers = {
    "Content-Type": "application/json"
}

# Function to fetch data for a specific year and team
def fetch_team_data(team_abbr, season):
    # Define the GraphQL query with variables
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
    
    # Define the variables
    variables = {
        "teamAbbr": team_abbr,
        "season": season
    }
    
    # Create the payload
    payload = {
        "query": query,
        "variables": variables
    }
    
    # Make the POST request
    response = requests.post(url, headers=headers, json=payload)
    
    # Check if the request was successful and return the response
    if response.status_code == 200:
        return response.json()  # Return the parsed JSON response
    else:
        print(f"Error: {response.status_code}")
        print(response.text)  # Print error message if available
        return None

