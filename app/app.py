import os
import json
from flask import Flask, render_template, request, redirect, url_for
from flask import send_from_directory
from helpers import Member, CustomJSONEncoder
from flask import jsonify
from datetime import datetime

app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

members_file_path = os.path.join(BASE_DIR, 'data', 'members.json')

with open(members_file_path) as f:
    members_data = json.load(f)

members = [Member(data['name'], data.get('adhesion_date'), data['contributions']) for data in members_data]


@app.route('/')
def home():
    page = request.args.get('page', 1, type=int)
    per_page = 10  # you can change this to display as many members as you want per page
    members_paginated = paginate(members, page, per_page)
    return render_template('index.html', members=members_paginated, page=page)


def paginate(data, page, per_page):
    offset = (page - 1) * per_page
    return data[offset : offset + per_page]

@app.route('/add_member', methods=['GET', 'POST'])
def add_member():
    if request.method == 'POST':
        name = request.form.get('name')
        new_member = Member(name, datetime.now().strftime('%d/%m/%Y %H:%M:%S'), [])
        members.append(new_member)
        # Also add the new member to the JSON file
        with open(members_file_path, 'w') as f:
            members_data.append({
                'name': name,
                'adhesion_date': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                'contributions': []})
            json.dump(members_data, f)
        return redirect(url_for('home'))
    return render_template('add_member.html')


@app.route('/update_member/<string:name>', methods=['GET', 'POST'])
def update_member(name):
    if request.method == 'POST':
        new_name = request.form['new_name']
        for member in members:
            if member.name == name:
                member.name = new_name

        # Persist the changes to the JSON file
        with open(members_file_path, 'w') as f:
            members_data = [{
                'name': member.name,
                'adhesion_date': member.adhesion_date.strftime('%Y-%m-%d %H:%M:%S'),
                'contributions': [{
                    'date': contribution['date'].strftime('%Y-%m-%d %H:%M:%S'),
                    'amount': contribution['amount']
                } for contribution in member.contributions]
            } for member in members]
            json.dump(members_data, f)

        return redirect(url_for('overview'))
    return render_template('update_member.html', name=name)


from flask import jsonify, make_response


@app.route('/delete_member/<string:name>', methods=['GET', 'POST'])
def delete_member(name):
    global members_data
    member = next((item for item in members_data if item["name"] == name), None)
    if member:
        members_data.remove(member)
        with open(members_file_path, 'w') as f:
            # Use a custom JSONEncoder to handle datetime objects
            json.dump(members_data, f, default=CustomJSONEncoder().default)
        return make_response(jsonify({"message": f'Member {name} deleted successfully'}), 200)
    else:
        return make_response(jsonify({"error": "Member not found"}), 404)


@app.route('/overview')
def overview():
    return render_template('overview.html', members=members)


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
            members = [Member(data['name'], data.get('adhesion_date'), data['contributions']) for data in
                       data_to_import]
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

        # After updating the members, write the changes back to the JSON file
        with open(members_file_path, 'w') as f:
            json.dump([member.to_dict() for member in members], f)

        return redirect(url_for('home'))
    return render_template('add_contribution.html', name=name)


@app.route('/total_contributions/<int:year>/<int:month>', methods=['GET'])
def get_total_contributions_by_month(year, month):
    total_contributions = []
    for member in members:
        total = 0
        for contribution in member.contributions:
            contribution_date = contribution['date']
            if contribution_date.year == year and contribution_date.month == month:
                total += contribution['amount']
        total_contributions.append({'name': member.name, 'total': total})
    return jsonify(total_contributions)


if __name__ == "__main__":
    app.run(debug=True)
