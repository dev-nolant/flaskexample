from flask import Flask, Response
import json
import os
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def display_json():
    try:
        # Get the current date in the format "month/day/year"
        current_date = datetime.now().strftime("%m-%d-%Y")

        # Construct the JSON file path with the date
        json_filename = f"data/combined_players_data_{current_date}.json"

        if not os.path.exists(json_filename):
            return "JSON file not found.", 404

        with open(json_filename, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
            pretty_json = json.dumps(data, indent=4)  # Pretty print the JSON
            return Response(pretty_json, content_type='application/json')
    except json.JSONDecodeError:
        return "Error decoding JSON.", 400

if __name__ == '__main__':
    app.run(debug=True)
