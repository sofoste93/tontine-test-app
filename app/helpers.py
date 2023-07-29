from datetime import datetime
from flask.json import JSONEncoder


def _convert_date_format(date_str):
    formats = ["%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%d/%m/%Y %H:%M:%S", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S"]
    for date_format in formats:
        try:
            return datetime.strptime(date_str, date_format)
        except ValueError:
            pass
    raise ValueError(f"time data {date_str} does not match any of the expected formats")


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, datetime.datetime):
                return obj.isoformat()
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)


class Member:
    def __init__(self, name, adhesion_date=None, contributions=None):
        self.name = name
        if adhesion_date is None:
            self.adhesion_date = datetime.now()
        else:
            self.adhesion_date = _convert_date_format(adhesion_date)
        if contributions:
            self.contributions = [{'amount': c['amount'], 'date': _convert_date_format(c['date'])} for c in
                                  contributions]
        else:
            self.contributions = []

    def to_dict(self):
        return {
            'name': self.name,
            'adhesion_date': self.adhesion_date.isoformat(),
            'contributions': [{'amount': c['amount'], 'date': c['date'].isoformat()} for c in self.contributions]
        }

    @property
    def total_contributions(self):
        return sum(contribution['amount'] for contribution in self.contributions)

    def add_contribution(self, amount, date=None):
        if date is None:
            date = datetime.now()
        if isinstance(date, str):
            date = datetime.strptime(date, '%d/%m/%Y %H:%M:%S')
        self.contributions.append({'amount': amount, 'date': date})
