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

from collections import OrderedDict
from flask import g
from py2neo import neo4j
from neo4jrestclient import client


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


def execute_query(query):
    res = neo4j.CypherQuery(g.neo4j_db, query)
    for record in res.stream():
        yield record


def execute_single_analysis_query(query, config, measure):
    result = OrderedDict()
    for node, relation in execute_query(query):
        word = node['identifier']
        result[word] = (Node(node, config), Relation(relation, measure))
    return result


def execute_contrastive_analysis_query(query, config, measure):
    result = OrderedDict()
    for node, relation_first_node, relation_second_node in execute_query(query):
        word = node['identifier']
        result[word] = (Node(node, config),
                        Relation(relation_first_node, measure),
                        Relation(relation_second_node, measure))
    return result