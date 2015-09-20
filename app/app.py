import os

import jinja2
from flask import Flask, render_template
from datetime import datetime, timedelta
from flask.ext.sqlalchemy import SQLAlchemy
from clarifai_basic import ClarifaiCustomModel

app = Flask(__name__)

@app.route("/")
def index():
    start = datetime.now() - timedelta(weeks=2)
    data = "get from file"
    return render_template('index.html', data=data)

@app.route("/clarifai")
def clarifai():
    clarifai = ClarifaiCustomModel()
    concept_name = 'piyali'
    PIYALI_POSITIVES = [
      'http://anshulkgupta.com/hackmit/piyali1.png',
      'http://anshulkgupta.com/hackmit/piyali2.png',
      'http://anshulkgupta.com/hackmit/piyali3.png',
      'http://anshulkgupta.com/hackmit/piyali4.png'
    ]
    for positive_example in PIYALI_POSITIVES:
      clarifai.positive(positive_example, concept_name)
    PIYALI_NEGATIVES = [
      'http://anshulkgupta.com/hackmit/anshul1.png',
      'http://anshulkgupta.com/hackmit/anshul2.png',
      'http://anshulkgupta.com/hackmit/annie1.png',
      'http://anshulkgupta.com/hackmit/annie2.png'
    ]
    for negative_example in PIYALI_NEGATIVES:
      clarifai.negative(negative_example, concept_name)
    clarifai.train(concept_name)
    PIYALI_TEST = [
      'http://anshulkgupta.com/hackmit/piyali-test1.png'
    ]
    NOT_PIYALI = [
      'http://anshulkgupta.com/hackmit/annie-test1.png',
      'http://anshulkgupta.com/hackmit/anshul-test1.png',
      'http://anshulkgupta.com/hackmit/anshul-test2.png'
    ]
    data = []
    for test in PIYALI_TEST + NOT_PIYALI:
        result = clarifai.predict(test, concept_name)
        data.append([result['status']['message'],
                    result['urls'][0]['score'],
                    result['urls'][0]['url']])
    return render_template('clarifai.html', data=data)

if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0")