from math import log
from py2neo import neo4j
from itertools import chain
from flask import g
from collections import OrderedDict

#TODO: Use clean keyword
from requestHelper import multiple_replace, vowel_dic


class Relation(dict):
    def __init__(self, rel, measure_to_use):
        super(Relation, self).__init__(self)
        self['edge_weight'] = rel['weight']
        self['measure'] = rel[measure_to_use]


class Node(dict):
    def __init__(self, node, app_config):
        super(Node, self).__init__(self)
        #For each node the dict is reversed TODO
        reverse_tags = {v: k for k, l in app_config['POS_TAGS'].items() for v in l}
        self['freq'] = node['frequency']
        self['word_class'] = reverse_tags[node['word_class']]
        self['name_entity'] = 'ja' if node['name_entity'] else 'nein'


def create_single_analysis(input_values, config):
    origin_keyword = input_values['keywords'][0].lower()
    keyword = multiple_replace(origin_keyword, vowel_dic)

    database_result = OrderedDict()
    query = create_single_query(keyword.lstrip(), input_values, input_values['limit'])

    for named_tuple in execute_query(query):
        node = named_tuple[0]
        rel = named_tuple[1]

        word = node['identifier']
        database_result[word] = (Node(node, config), Relation(rel, input_values['measure']))

    return database_result


def create_contrastive_analysis(input_values, config):
    keywords = [multiple_replace(k.lower(), vowel_dic) for k in input_values['keywords']]

    overlap_limit = int(input_values['overlap_limit'] / 100 * input_values['limit'])

    overlap = OrderedDict()
    overlap_query = create_overlap_query(keywords[0], keywords[1], input_values, input_values['limit'])
    for named_tuple in execute_query(overlap_query):
        node = named_tuple[0]
        rel1 = named_tuple[1]
        rel2 = named_tuple[2]

        word = node['identifier']
        overlap[word] = (
            Node(node, config), Relation(rel1, input_values['measure']), Relation(rel2, input_values['measure']))

    global_limit = (input_values['limit'] - min(overlap_limit, len(overlap))) // 2

    results = []
    for k in keywords:
        term = OrderedDict()
        single_query = create_single_query(k, input_values, global_limit, list(overlap.keys()))
        for named_tuple in execute_query(single_query):
            node = named_tuple[0]
            rel = named_tuple[1]

            word = node['identifier']
            term[word] = (Node(node, config), Relation(rel, input_values['measure']))
        results.append(term)

    tmp = OrderedDict()
    for i, t in enumerate(overlap.items()):
        if i >= overlap_limit:
            break
        k, v = t
        tmp[k] = v

    overlap = tmp

    labels = list(results[0].keys()) + list(overlap.keys()) + list(results[1].keys())[::-1]

    tmp = OrderedDict()
    for k, v in overlap.items():
        results[0][k] = (v[0], v[1])
        tmp[k] = (v[0], v[2])

    for k, v in results[1].items():
        tmp[k] = (v[0], v[1])

    results[1] = tmp

    max_value = max(chain(results[0].values(), results[1].values()), key=lambda k: k[1]['measure'])[1]['measure']
    min_value = min(chain(results[0].values(), results[1].values()), key=lambda k: k[1]['measure'])[1]['measure']


    data = [[transform_to_logistic_curve(results[0].get(t)[1]['measure'], max_value, min_value)
             if t in results[0] else {'y': 0, 'org_y': 0} for t in labels],
            [transform_to_logistic_curve(results[1].get(t)[1]['measure'], max_value, min_value)
             if t in results[1] else {'y': 0, 'org_y': 0} for t in labels]]

    max_value_new = max(chain(data[0], data[1]), key=lambda k: k['y'])['y']
    min_value_new = min(chain(data[0], data[1]), key=lambda k: k['y'])['y']

    #Oder müssen das hier die min und max der neuen daten sein?
    small_point = int((max_value - abs(min_value)) * 0.03)

    tmp1 = [{'y': max(scale(d['y'], max_value, min_value, max_value_new, min_value_new), small_point), 'org_y': d['org_y']}
            if d['org_y'] != 0 else {'y': 0, 'org_y': 0} for d in data[0]]
    tmp2 = [{'y': max(scale(d['y'], max_value, min_value, max_value_new, min_value_new), small_point) * -1, 'org_y': d['org_y']}
            if d['org_y'] != 0 else {'y': 0, 'org_y': 0} for d in data[1]]

    data = [tmp1, tmp2]

    return labels, data, results


def scale(x, origin_max, origin_min, transform_max, transform_min):
        if x == 0:
            return 0
        m = (origin_max - origin_min) / (transform_max - transform_min)
        return m * x + origin_min - m * transform_min


def transform_to_logistic_curve(value, max_v, min_v):
    def logic(x):
        return 0 if x == 0 else -log(1/x - 1)

    #Note this will maybe return 0 values
    transformed_value = (value - min_v) / max_v
    return {'y': logic(transformed_value), 'org_y': value}


def create_single_query(keyword, input_values, limit, exclude=[]):
    ner = [1] if input_values['opts']['only_names'] else [0, 1]
    query = "START a = node:TokenNode(identifier=\"{0}\") match a-[r:{1}]-b where r.{2} > 0 and r.weight >= {3} and " \
            "b.frequency >= {4} and b.name_entity in {5} and b.word_class in {6} and not(b.identifier in {7}) RETURN  b, r " \
            "order by r.{2} desc limit {8} ".format(keyword, input_values['rel'], input_values['measure'],
                                                    input_values['edge_weight'], input_values['freq_a'], ner,
                                                    input_values['allowed_word_classes'],
                                                    input_values['exclude_list'] + exclude, limit)
    return query


def create_overlap_query(k1, k2, input_values, limit):
    ner = [1] if input_values['opts']['only_names'] else [0, 1]
    query = "START a = node:TokenNode(identifier=\"{0}\"), b = node:TokenNode(identifier=\"{1}\") match a-[x:{2}]-c-[y:{2}]-b " \
            "where x.{3} > 0 and y.{3} > 0 and x.weight >= {4} and y.weight >= {4} and " \
            "c.frequency >= {5} and c.name_entity in {6} and c.word_class in {7} and not(c.identifier in {8}) RETURN  c, x, y " \
            "order by x.{3} desc limit {9}".format(k1, k2, input_values['rel'], input_values['measure'],
                                                   input_values['edge_weight'], input_values['freq_ab'], ner,
                                                   input_values['allowed_word_classes'],
                                                   input_values['exclude_list'], limit)

    return query


def execute_query(query):
    res = neo4j.CypherQuery(g.neo4j_db, query)
    for record in res.stream():
        yield record



