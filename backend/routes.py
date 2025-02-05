from flask import request, redirect, url_for, jsonify, send_from_directory
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.processing.parse_player_stats import get_filtered_player_data, get_mvp_data, calculate_score
from backend.processing.team_stats import get_team_stats_by_year, get_team

def register_routes(app):
    @app.route('/result', methods=['GET'])
    def result():
        team_year_stats = request.args.get('year')
        lwr_points = request.args.get('lwr_points', '15')
        lwr_points = float(lwr_points.strip()) if lwr_points.strip() else 15.0

        lwr_efg = request.args.get('lwr_efg', '40')
        lwr_efg = float(lwr_efg.strip()) * 0.01 if lwr_efg.strip() else 0.4

        lwr_gs = request.args.get('lwr_gs', '50')
        lwr_gs = int(lwr_gs.strip()) if lwr_gs.strip() else 50

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
            unique_result_data = list({player['Player']: player for player in result_data_sorted}.values())

            return jsonify(unique_result_data)

        except Exception as e:
            return jsonify({"error": f"Error processing player stats: {e}"}), 500

    @app.route('/static/<path:path>')
    def serve_static(path):
        return send_from_directory(os.path.join(app.root_path, 'static'), path)
