import os

from flask import Flask, render_template
from datetime import datetime, timedelta
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)

@app.route("/")
def index():
    start = datetime.now() - timedelta(weeks=2)
    data = "get from file"
    return render_template('index.html', data=data)

if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0")