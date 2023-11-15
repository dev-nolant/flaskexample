from flask import Flask, jsonify
import json

app = Flask(__name__)

@app.route('/')
def display_json():
    try:
        with open('combined_players_data.json', 'r', encoding='utf-8') as json_file:  # Replace 'yourfile.json' with your JSON file
            data = json.load(json_file)
            return jsonify(data)
    except FileNotFoundError:
        return "JSON file not found.", 404
    except json.JSONDecodeError:
        return "Error decoding JSON.", 400

if __name__ == '__main__':
    app.run(debug=True)
