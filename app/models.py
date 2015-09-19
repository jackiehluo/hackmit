from datetime import datetime

from app import db

class Person(db.Model):

    __tablename__ = "people"

    id = db.Column(db.Integer, primary_key=True)
    visit_time = db.Column(db.DateTime, nullable=False)

    def __init__(self):
        self.visit_time = datetime.now()