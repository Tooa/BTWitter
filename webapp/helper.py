import re
from math import log, exp
from json import loads
from itertools import chain
from py2neo import neo4j
from flask import g
from collections import OrderedDict

vowel_dic = {'ä': 'ae', 'Ä': 'ae', 'ü': 'ue', 'Ü': 'ue', 'Ö': 'oe', 'ö': 'oe', 'ß': 'ss', 'ẞ': 'ss'}


def multiple_replace(text, dic):
    # Note this implementation uses a single pass and ignores letter case!
    regex = re.compile(r"|".join(map(re.escape, list(dic.keys()))))
    return regex.sub(lambda mo: dic[mo.group(0)], text)


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

    context_list = [(x, keywords[0:1]) for x in list(results[0].keys())] + \
                   [(x, keywords) for x in list(overlap.keys())] + \
                   [(x, keywords[1:2]) for x in list(results[1].keys())[::-1]]

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

    return labels, data, context_list, results


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

    #max(value, int(max_v * 0.05))
    #log(value, 10)

    #return {'y': logic(new_v) * modifier, 'org_y': value}
    #return log(value) * modifier


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
    res = neo4j.CypherQuery(g.db, query)
    for record in res.stream():
        yield record


def input_is_valid(request_values):
    def first_keyword_is_not_empty():
        return request_values['keywords'] and request_values['keywords'][0] != ''

    def any_word_class_selected():
        return any(request_values['pos'].values())

    return first_keyword_is_not_empty() and request_values['limit'] > 0 and any_word_class_selected()


class RequestValues(dict):
    def __init__(self, request, app_config):
        super(RequestValues, self).__init__(self)
        self['exclude_list'] = loads(request['exclude'])
        self['keywords'] = [x.strip() for x in loads(request['keywords'])]
        self['measure'] = request['measure']
        self['limit'] = int(request['limit'])
        self['overlap_limit'] = int(request['overlap_limit'])
        self['edge_weight'] = int(request['edge_weight'])
        self['freq_a'] = int(request['freq_a'])
        self['freq_b'] = int(request['freq_b'])
        self['freq_ab'] = int(request['freq_ab'])
        #Only necessary for rel, maybe remove
        self['opts'] = loads(request['opts'])
        self['rel'] = 'AFTER' if self['opts']['include'] else 'BEFORE'
        #Only necessary for allowed_word_classes
        self['pos'] = loads(request['pos'])
        self['allowed_word_classes'] = list(chain.from_iterable(app_config['POS_TAGS'][k] for k in
                                                                self['pos'] if self['pos'][k]))


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
