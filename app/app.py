import os
import json
from flask import Flask, render_template
from helpers import Member

app = Flask(__name__)

# Get the absolute path to the parent directory of this file (app.py)
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# Use os.path.join to generate the path to the members.json file
members_file_path = os.path.join(BASE_DIR, 'data', 'members.json')

# Load members data from JSON file
with open(members_file_path) as f:
    members_data = json.load(f)

# Convert dictionaries to Member objects
members = [Member(data['name'], data['contributions']) for data in members_data]


@app.route('/')
def home():
    # Pass members data to the template
    return render_template('index.html', members=members)


if __name__ == "__main__":
    app.run(debug=True)
