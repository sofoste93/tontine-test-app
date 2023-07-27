import os
import json
from flask import Flask, render_template, request, redirect, url_for
from flask import send_from_directory
from helpers import Member
from flask import jsonify
from datetime import datetime

app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

members_file_path = os.path.join(BASE_DIR, 'data', 'members.json')

with open(members_file_path) as f:
    members_data = json.load(f)

members = [Member(data['name'], data['contributions']) for data in members_data]


@app.route('/')
def home():
    return render_template('index.html', members=members)


@app.route('/add_member', methods=['GET', 'POST'])
def add_member():
    if request.method == 'POST':
        name = request.form.get('name')
        new_member = Member(name, [])
        members.append(new_member)
        # Also add the new member to the JSON file
        with open(members_file_path, 'w') as f:
            members_data.append({'name': name, 'contributions': []})
            json.dump(members_data, f)
        return redirect(url_for('home'))
    return render_template('add_member.html')


@app.route('/export_data')
def export_data():
    with open(members_file_path, 'w') as f:
        data_to_export = [
            {
                'name': member.name,
                'contributions': [{'amount': c['amount'], 'date': c['date'].strftime('%d/%m/%Y %H:%M:%S')} for c in
                                  member.contributions]
            }
            for member in members
        ]
        json.dump(data_to_export, f)
    return send_from_directory(BASE_DIR, 'data/members.json', as_attachment=True)


@app.route('/import_data', methods=['GET', 'POST'])
def import_data():
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.json'):
            data_to_import = json.load(file)
            global members
            members = [Member(data['name'], data['contributions']) for data in data_to_import]
            with open(members_file_path, 'w') as f:
                json.dump(data_to_import, f)
            return redirect(url_for('home'))
    return render_template('import_data.html')


@app.route('/add_contribution/<string:name>', methods=['GET', 'POST'])
def add_contribution(name):
    if request.method == 'POST':
        amount = request.form['amount']
        date = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        for member in members:
            if member.name == name:
                member.add_contribution(float(amount), date)
        return redirect(url_for('home'))
    return render_template('add_contribution.html', name=name)


@app.route('/total_contributions/<int:year>/<int:month>', methods=['GET'])
def get_total_contributions_by_month(year, month):
    total_contributions = []
    for member in members:
        total = 0
        for contribution in member.contributions:
            contribution_date = datetime.strptime(contribution['date'], '%d/%m/%Y %H:%M:%S')
            if contribution_date.year == year and contribution_date.month == month:
                total += contribution['amount']
        total_contributions.append({'name': member.name, 'total': total})
    return jsonify(total_contributions)


if __name__ == "__main__":
    app.run(debug=True)
