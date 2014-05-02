class ProductiveConfig(object):

    UPLOAD_FOLDER = 'btwitter/upload'
    ALLOWED_EXTENSIONS = set(['co_s', 'words', 'postags', 'ner'])

    GRAPH_DB_URI = 'http://localhost:7474/db/data/'
    POSTGRE_SQL_URI = 'dbname=corpus host=localhost user=tiny password=tiny'

    SIGNIFICANCE_MEASURES = [('lldivlognAB', 'log-likelihood / log(nAB)'),
                             ('ll', 'log-likelihood'), ('lldivnAB', 'log-likelihood / nAB'),
                             ('pmi', 'Pointwise mutual information'),
                             ('lmi', 'Lexical mutual information')]

    POS_TAGS = {
        'hash': [-1],
        'adjektiv': [2],
        'user': [-2],
        'nomen': [4, 7],
        'verb': [3, 5, 15, 22],
        'standorte': [12, 8, 13],
        'sonstige': [0, 6, 9, 10, 11, 14, 16, 17, 18, 19, 20, 21, 23, 24, 25, 26, 27, 28, 29, 30]
    }


