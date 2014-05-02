# -*- coding: utf-8 -*-
from json import loads
import os
from itertools import chain
from flask import Flask, render_template, request, jsonify, g
from py2neo import neo4j
import psycopg2
import subprocess

from helper import multiple_replace, vowel_dic, RequestValues, create_contrastive_analysis, create_single_analysis, \
    input_is_valid


def create_app():
    app = Flask(__name__)

    app.secret_key = os.urandom(24)
    app.config.from_object('config.Config')

    @app.before_request
    def before_request():
        g.db = neo4j.GraphDatabaseService(app.config['GRAPH_DB_URI'])
        g.pgDB = psycopg2.connect(app.config['POSTGRE_SQL_URI'])

    @app.route("/", methods=['GET', 'POST'])
    @app.route('/index')
    def index():
        return render_template(
            'index.jinja2', measures=app.config['SIGNIFICANCE_MEASURES'],
            pos_tags=app.config['POS_TAGS'].keys())

    def save_file(file, save_name):
        def allowed_file(filename):
            return '.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

        if file and allowed_file(file.filename):
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], save_name))

    @app.route('/import', methods=['GET', 'POST'])
    def import_data():
        if not app.config['DEBUG']:
            return "Access denied"

        if request.method == 'POST':

            upload_folder = app.config['UPLOAD_FOLDER']

            save_file(request.files['file1'], 'before_words')
            save_file(request.files['file2'], 'after_words')
            save_file(request.files['file3'], 'before_rel')
            save_file(request.files['file4'], 'after_rel')
            save_file(request.files['file5'], 'postags')
            save_file(request.files['file6'], 'multiwords')

            subprocess.call(
                ['python3.3', 'convert.py',
                 os.path.join(upload_folder, 'before_words'),
                 os.path.join(upload_folder, 'before_rel'),
                 os.path.join(upload_folder, 'corpus_before'),
                 os.path.join(upload_folder, 'corpus_before'), 'BEFORE'])

            subprocess.call(
                ['python3.3', 'convert.py',
                 os.path.join(upload_folder, 'after_words'),
                 os.path.join(upload_folder, 'after_rel'),
                 os.path.join(upload_folder, 'corpus_after'),
                 os.path.join(upload_folder, 'corpus_after'), 'AFTER'])

            os.remove(os.path.join(upload_folder, 'before_words'))
            os.remove(os.path.join(upload_folder, 'after_words'))
            os.remove(os.path.join(upload_folder, 'before_rel'))
            os.remove(os.path.join(upload_folder, 'after_rel'))
            os.remove(os.path.join(upload_folder, 'postags'))
            os.remove(os.path.join(upload_folder, 'multiwords'))

            subprocess.call(
                ['import2Neo4j.sh',
                 os.path.join(upload_folder, 'corpus_after.nodes.gz'),
                 os.path.join(upload_folder, 'corpus_after.relation.gz'),
                 os.path.join(upload_folder, 'corpus_before.relation.gz')])

            return "Import Done"

        return render_template('import.jinja2')


    #TODO Rename: get_context()
    @app.route("/getContext", methods=('POST',))
    def getContext():
        def query(keyword, term, cursor):
            cursor.execute("""select S.sentence from sentences S where S.id in
                        (select sentenceId from inv_w I where
                        I.wordId in (select id from words where word IN (%s, %s))
                        group by I.sentenceId
                        having count(distinct I.wordId) = 2
                        );""", (keyword, term))
            return cursor.fetchall()

        values = request.values
        keyword = loads(values['keyword'])
        cooccurrence = values['cooccurrence']

        cur = g.pgDB.cursor()
        result = query(multiple_replace(keyword.lower(), vowel_dic), cooccurrence, cur)
        cur.close()
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
            context_list = [(l, input_values['keywords'][0:]) for l in labels]
        # Constrastive Analysis
        elif len(input_values['keywords']) == 2:
            labels, data, context_list, database_result = create_contrastive_analysis(input_values, app.config)

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

        return jsonify(series=series, title=title, yAxis=y_axis, labels=labels, context_list=context_list,
                       info={key: value for (key, value) in zip(input_values['keywords'], database_result)},
                       exclude=True if input_values['exclude_list'] else False)

    return app

