from flask import Flask, Response
import json

app = Flask(__name__)

@app.route('/')
def display_json():
    try:
        with open('combined_players_data.json', 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
            pretty_json = json.dumps(data, indent=4)  # Pretty print the JSON
            return Response(pretty_json, content_type='application/json')
    except FileNotFoundError:
        return "JSON file not found.", 404
    except json.JSONDecodeError:
        return "Error decoding JSON.", 400

if __name__ == '__main__':
    app.run(debug=True)
