# -*- coding: utf-8 -*-
from flask import Flask, send_file, render_template, jsonify
from flask.ext.dataset import Dataset

import tagging
import db
import analyze


app = Flask(__name__)
app.config.from_object('default_settings')
database = Dataset(app)


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/interviews.json")
def interviews_json():
    table = db.interviews_table(database)
    interviews = list(map(format_row, table.find()))
    return jsonify(
        interviews=interviews,
        scorecard_recs=analyze.REC_SCORES,
    )


def format_row(row):
    interview = dict(row)
    interview['scorecard_tags'] = list(tagging.split_tags(interview['scorecard_tags']))
    return interview


@app.route("/interviews.db")
def interviews_db():
    return send_file('data/interviews.db')


if __name__ == "__main__":
    app.run(debug=True)
