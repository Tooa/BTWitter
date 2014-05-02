# -*- coding: utf-8 -*-
from json import loads
import os
from itertools import chain
from flask import Flask, render_template, request, jsonify, g
from py2neo import neo4j
import psycopg2

from databaseImport import do_import
from requestHelper import clean_keyword, RequestValues, input_is_valid

from analysis import create_contrastive_analysis, create_single_analysis


def create_app():
    app = Flask(__name__)

    app.secret_key = os.urandom(24)
    app.config.from_object('config.ProductiveConfig')

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
            do_import(request, app.config['UPLOAD_FOLDER'], app.config['ALLOWED_EXTENSIONS'])
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

        if not input_is_valid(input_values):
            return jsonify(series=[], title={"text": 'NO DATA'}, xAxis={}, yAxis={}, labels=[], context_list=[],
                           info={}, exclude=[])

        # Single Analysis
        if len(input_values['keywords']) == 1:
            database_result = create_single_analysis(input_values, app.config)

            if len(database_result) <= 0:
                return jsonify(series=[], title={"text": 'NO DATA'}, xAxis={}, yAxis={}, labels=[], context_list=[],
                               info={}, exclude=[])

            labels = list(database_result.keys())
            data = [t[1]['measure'] for t in database_result.values()]

            database_result = [database_result]

            series = [{"name": input_values['keywords'][0], "data": [{'y': t, 'org_y': t} for t in data]}]
            y_axis = {"min": min(data), "max": max(data), "type": 'logarithmic'}
        # Constrastive Analysis
        elif len(input_values['keywords']) == 2:
            labels, data, database_result = create_contrastive_analysis(input_values, app.config)

            #Codeduplication how?
            if len(database_result) <= 0:
                return jsonify(series=[], title={"text": 'NO DATA'}, xAxis={}, yAxis={}, labels=[], context_list=[],
                               info={}, exclude=[])

            series = [{"name": input_values['keywords'][0], "data": data[0]},
                      {"name": input_values['keywords'][1], "data": data[1]}]
            y_axis = {"min": min(chain(data[0], data[1]), key=lambda k: k['y'])['y'],
                      "max": max(chain(data[0], data[1]), key=lambda k: k['y'])['y']}

        else:
            print('error unknown len of keywords')

        title = {"text": 'Chart for the keywords:  ' + str(input_values['keywords'])}

        return jsonify(series=series, title=title, yAxis=y_axis, labels=labels,
                       info={key: value for (key, value) in zip(input_values['keywords'], database_result)},
                       exclude=True if input_values['exclude_list'] else False)

    return app

