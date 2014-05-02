from flask import g
from py2neo import neo4j


def execute_query(query):
    res = neo4j.CypherQuery(g.neo4j_db, query)
    for record in res.stream():
        yield record


def create_single_query(keyword, input_values, limit, exclude=[]):
    ner = [1] if input_values['opts']['only_names'] else [0, 1]
    query = "START a = node:TokenNode(identifier=\"{0}\") match a-[r:{1}]-b where r.{2} > 0 and r.weight >= {3} and " \
            "b.frequency >= {4} and b.name_entity in {5} and b.word_class in {6} and not(b.identifier in {7}) RETURN  b, r " \
            "order by r.{2} desc limit {8} ".format(keyword, input_values['rel'], input_values['measure'],
                                                    input_values['edge_weight'], input_values['freq_a'], ner,
                                                    input_values['allowed_word_classes'],
                                                    input_values['exclude_list'] + exclude, limit)
    return query


def create_overlap_query(k1, k2, input_values):
    ner = [1] if input_values['opts']['only_names'] else [0, 1]
    query = "START a = node:TokenNode(identifier=\"{0}\"), b = node:TokenNode(identifier=\"{1}\") match a-[x:{2}]-c-[y:{2}]-b " \
            "where x.{3} > 0 and y.{3} > 0 and x.weight >= {4} and y.weight >= {4} and " \
            "c.frequency >= {5} and c.name_entity in {6} and c.word_class in {7} and not(c.identifier in {8}) RETURN  c, x, y " \
            "order by x.{3} desc limit {9}".format(k1, k2, input_values['rel'], input_values['measure'],
                                                   input_values['edge_weight'], input_values['freq_ab'], ner,
                                                   input_values['allowed_word_classes'],
                                                   input_values['exclude_list'], input_values['limit'])

    return query