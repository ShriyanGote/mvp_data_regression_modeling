from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_cors import CORS
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from calculations.player_stats import get_filtered_player_data, get_mvp_data, calculate_score
from calculations.team_stats import get_team_stats_by_year, get_team

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/result', methods=['GET'])
def result():
    team_year_stats = request.args.get('year')
    lwr_points = request.args.get('lwr_points', '15')  # Default as string '15'
    lwr_points = float(lwr_points) if lwr_points.strip() else 15.0  # Convert to float or use default

    lwr_efg = request.args.get('lwr_efg', '40')  # Default as string '40'
    lwr_efg = float(lwr_efg) * 0.01 if lwr_efg.strip() else 0.4  # Convert to fraction or use default

    lwr_gs = request.args.get('lwr_gs', '50')  # Default as string '50'
    lwr_gs = int(lwr_gs) if lwr_gs.strip() else 50  # Convert to int or use default

    if not team_year_stats:
        return redirect(url_for('index'))

    try:
        all_teams = get_team_stats_by_year(team_year_stats)
        filtered_player_data, mvp = get_filtered_player_data(team_year_stats, lwr_points, lwr_gs, lwr_efg)
        result_data = []
        for name in filtered_player_data['Player']:
            player = get_mvp_data(filtered_player_data, name)
            if player is None:
                continue 

            player_team = get_team(all_teams, str(player[2]))
            if not player_team:
                continue

            player_fullstats = list(player) + [player_team['Wins'], player_team['Rank']]
            result_data.append({
                'Player': name,
                'MVP Score': round(calculate_score(player_fullstats), 2),
                'MVP': (name == mvp)
            })

        result_data_sorted = sorted(result_data, key=lambda x: x['MVP Score'], reverse=True)
        unique_result_data = {player['Player']: player for player in result_data_sorted}.values()

        return jsonify(list(unique_result_data))  # Return JSON for React
    
    except Exception as e:
        return jsonify({"error": f"Error processing player stats: {e}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
