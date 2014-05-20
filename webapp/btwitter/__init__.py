# -*- coding: utf-8 -*-
"""Copyright 2014 Uli Fahrer

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License."""

from json import loads
import os
from itertools import chain
from flask import Flask, render_template, request, jsonify, g
from py2neo import neo4j
import psycopg2

from databaseImport import do_import
from requestHelper import clean_keyword, RequestValues
from analysisHelper import maximum, minimum

from analysis import create_contrastive_analysis, create_single_analysis


app = Flask(__name__)

app.secret_key = os.urandom(24)
app.config.from_object('config.ProductiveConfig')
app.config['PROPAGATE_EXCEPTIONS'] = True

@app.before_request
def before_request():
    g.neo4j_db = neo4j.GraphDatabaseService(app.config['GRAPH_DB_URI'])
    g.posgre_db = psycopg2.connect(app.config['POSTGRE_SQL_URI'])


@app.route("/", methods=['GET', 'POST'])
@app.route('/index')
def index():
    return render_template('index.jinja2', measures=app.config['SIGNIFICANCE_MEASURES'],
                           pos_tags=app.config['POS_TAGS'].keys())


@app.route('/import', methods=['GET', 'POST'])
def import_data():
    if not app.config['DEBUG']:
        return "Access denied"

    if request.method == 'POST':
        do_import(request, app.config)
        return "Import Done"

    return render_template('import.jinja2')


@app.route("/get_context", methods=('POST',))
def get_context():
    keyword = clean_keyword(loads(request.values['keyword']))
    co_occurring_word = request.values['cooccurrence']

    cursor = g.posgre_db.cursor()
    cursor.execute("""select S.sentence from sentences S where S.id in
                    (select sentenceId from inv_w I where
                    I.wordId in (select id from words where word IN (%s, %s))
                    group by I.sentenceId
                    having count(distinct I.wordId) = 2
                    );""", (keyword, co_occurring_word))

    result = cursor.fetchall()
    cursor.close()
    return jsonify(tweets=result)


@app.route("/generate_chart", methods=('POST',))
def generate_chart():
    input_values = RequestValues(request.values, app.config)

    title = {"text": 'Kollokationsanalyse für:  ' + str(input_values['keywords'])}
    y_axis = {}
    series = []

    if len(input_values['keywords']) == 1:
        labels, data, database_result = create_single_analysis(input_values, app.config)
        y_axis['type'] = "logarithmic"
    elif len(input_values['keywords']) == 2:
        labels, data, database_result = create_contrastive_analysis(input_values, app.config)
    else:
        print('error unknown len of keywords')

    for keyword, d in zip(input_values['keywords'], data):
        series.append({"name": keyword, "data": d})

    measure = list(map(lambda k: k['y'], chain(*data)))

    y_axis['min'] = minimum(measure)
    y_axis['max'] = maximum(measure)

    if all(not d for d in database_result):
        return jsonify(series=[], title={"text": 'Keine Daten'}, xAxis={}, yAxis={}, labels=[], context_list=[],
                       info={}, exclude=[])

    return jsonify(series=series, title=title, yAxis=y_axis, labels=labels,
                   info={key: value for (key, value) in zip(input_values['keywords'], database_result)},
                   exclude=True if input_values['exclude_list'] else False)
