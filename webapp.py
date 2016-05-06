# -*- coding: utf-8 -*-
from flask import (Flask, current_app,
                   send_file, render_template, jsonify,
                   json)
from flask.ext.dataset import Dataset

import scorecard
import db
import analyze
from decorators import requires_auth


app = Flask(__name__)
app.config.from_object('default_settings')
database = Dataset(app)


@app.route("/")
@requires_auth
def index():
    return render_template('index.html')


@app.route("/interviews.json")
@requires_auth
def interviews_json():
    table = db.interviews_table(database)
    interviews = list(map(format_row, table.find()))
    return jsonify(
        interviews=interviews,
        scorecard_recs=analyze.REC_SCORES,
    )


def format_row(row):
    interview = dict(row)
    interview['scorecard_questions'] = json.loads(row['scorecard_questions'])
    interview['scorecard_ratings'] = json.loads(row['scorecard_ratings'])
    interview['scorecard_tags'] = list(scorecard.extract_tags(
        interview['scorecard_questions'],
        tags_prefix=current_app.config['TAGS_PREFIX'],
        question_title_re=current_app.config['TAGS_QUESTION_RE']))
    return interview


@app.route("/interviews.db")
@requires_auth
def interviews_db():
    return send_file('data/interviews.db')


if __name__ == "__main__":
    app.run(debug=True)
