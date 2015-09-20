import os

from flask import Flask, render_template
from datetime import datetime, timedelta
from flask.ext.sqlalchemy import SQLAlchemy


app = Flask(__name__)
db = SQLAlchemy(app)

from models import Person

@app.route("/")
def index():
    start = datetime.now() - timedelta(weeks=2)
    data = Person.query.filter(_and(Person.visit_time >= start)).all()
    return render_template('index.html',
                            data=data)

if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0")