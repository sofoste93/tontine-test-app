from datetime import datetime


class Member:
    def __init__(self, name, contributions=None):
        self.name = name
        self.contributions = contributions if contributions else []

    @property
    def total_contributions(self):
        return sum(contribution['amount'] for contribution in self.contributions)

    def add_contribution(self, amount):
        self.contributions.append({'amount': float(amount), 'date': datetime.now().isoformat()})

