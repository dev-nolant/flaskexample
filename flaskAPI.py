from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)
current_date = datetime.now().strftime("%m-%d-%Y")
# Path to the JSON data file
JSON_DATA_FILE = f'data/combined_players_data_{current_date}.json'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data', methods=['GET'])
def get_data():
    data = read_nba_data()
    return jsonify(data)

@app.route('/player-average', methods=['POST'])
def player_average():
    data = request.json
    player_name = data.get('player_name')
    stat = data.get('stat')
    nba_data = read_nba_data()
    average = calculate_player_average(nba_data, player_name, stat)
    return jsonify({"average": average})

@app.route('/dropdown-data', methods=['GET'])
def dropdown_data():
    try:
        nba_data = read_nba_data()
        if not nba_data:
            return jsonify({"error": "Data not found"}), 404

        player_names = [player.get('name') for player in nba_data if player.get('name')]
        return jsonify(sorted(set(player_names)))
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500

@app.route('/dropdown-data/<selected_player>', methods=['GET'])
def dropdown_data_for_player(selected_player):
    try:
        nba_data = read_nba_data()
        if not nba_data:
            return jsonify({"error": "Data not found"}), 404

        selected_player_data = next((player for player in nba_data if player.get('name') == selected_player), None)
        if selected_player_data:
            # Assuming 'gamelog_summary' is the key for game log data
            gamelog_summary = selected_player_data.get('gamelog_summary', [])
            return jsonify({"gamelog_summary": gamelog_summary})
        else:
            return jsonify({"error": "Player not found"}), 404
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500

@app.route('/teams', methods=['GET'])
def teams():
    try:
        nba_data = read_nba_data()
        if not nba_data:
            return jsonify({"error": "Data not found"}), 404

        teams = [player.get('team') for player in nba_data if player.get('team')]
        return jsonify(sorted(set(teams)))
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500

@app.route('/gamelog/<player_name>', methods=['GET'])
def gamelog(player_name):
    try:
        nba_data = read_nba_data()
        if not nba_data:
            return jsonify({"error": "Data not found"}), 404

        selected_player_data = next((player for player in nba_data if player.get('name') == player_name), None)
        if selected_player_data:
            gamelog_summary = selected_player_data.get('gamelog_summary', [])
            return jsonify(gamelog_summary)
        else:
            return jsonify({"error": "Player not found"}), 404
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500

@app.route('/players-by-team', methods=['GET'])
def players_by_team():
    try:
        nba_data = read_nba_data()
        if not nba_data:
            return jsonify({"error": "Data not found"}), 404

        teams = {}
        for player in nba_data:
            team = player.get('team')
            if team:
                if team not in teams:
                    teams[team] = []
                teams[team].append(player.get('name'))
        
        return jsonify(teams)
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500


@app.route('/opponents', methods=['GET'])
def opponents():
    try:
        nba_data = read_nba_data()
        if not nba_data:
            return jsonify({"error": "Data not found"}), 404

        opponents = [player.get('opponent') for player in nba_data if player.get('opponent')]
        return jsonify(sorted(set(opponents)))
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500

def read_nba_data():
    try:
        if os.path.exists(JSON_DATA_FILE):
            with open(JSON_DATA_FILE, 'r', encoding='utf8') as file:
                return json.load(file)
        else:
            return []
    except Exception as e:
        return []

def calculate_player_average(data, player_name, stat):
    total = 0.0
    count = 0
    for player in data:
        if player.get('name') == player_name:
            stat_value = player.get(stat, 0)
            try:
                total += float(stat_value)
                count += 1
            except ValueError:
                continue  # Ignore invalid values
    return total / count if count > 0 else None

if __name__ == '__main__':
    app.run(debug=True)
