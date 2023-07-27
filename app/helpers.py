from datetime import datetime


def _convert_date_format(date_str):
    try:
        # Try to parse the date with the new format
        return datetime.strptime(date_str, '%d/%m/%Y %H:%M:%S')
    except ValueError:
        # If it fails, try with the old format
        return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')


class Member:
    def __init__(self, name, contributions=None):
        self.name = name
        if contributions:
            self.contributions = [{'amount': c['amount'], 'date': _convert_date_format(c['date'])} for c in
                                  contributions]
        else:
            self.contributions = []

    @property
    def total_contributions(self):
        return sum(contribution['amount'] for contribution in self.contributions)

    def add_contribution(self, amount, date=None):
        if date is None:
            date = datetime.now()
        if isinstance(date, str):
            date = datetime.strptime(date, '%d/%m/%Y %H:%M:%S')
        self.contributions.append({'amount': amount, 'date': date})

