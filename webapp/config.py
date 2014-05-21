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


class ProductiveConfig(object):

    UPLOAD_FOLDER = 'btwitter/upload'
    ALLOWED_EXTENSIONS = set(['co_s', 'words', 'postags', 'ner'])

    POSTGRE_USER = 'tiny'
    POSTGRE_DB = 'corpus'
    POSTGRE_PASS = 'tiny'

    GRAPH_DB_URI = 'http://localhost:7474/db/data/'
    POSTGRE_SQL_URI = 'dbname=' + POSTGRE_DB + ' host=localhost user=' + POSTGRE_USER + ' password=' + POSTGRE_PASS

    SIGNIFICANCE_MEASURES = [('lldivlognAB', 'log-likelihood / log(nAB)'),
                             ('ll', 'log-likelihood'), ('lldivnAB', 'log-likelihood / nAB'),
                             ('pmi', 'Pointwise mutual information'),
                             ('lmi', 'Lexical mutual information')]

    POS_TAGS = {
        'hashtags': [-1],
        'adjektive': [2],
        'usernamen': [-2],
        'nomen': [4, 7],
        'verben': [3, 5, 15, 22],
        'standorte': [12, 8, 13],
        'sonstige': [0, 6, 9, 10, 11, 14, 16, 17, 18, 19, 20, 21, 23, 24, 25, 26, 27, 28, 29, 30]
    }


