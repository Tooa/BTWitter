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

from itertools import chain

from analysisQuery import create_single_query, create_overlap_query, execute_single_analysis_query, \
    execute_contrastive_analysis_query
from analysisHelper import transform_to_logistic_curve, rescale, remove_overlap_excess, append_overlap, maximum, minimum
from requestHelper import clean_keyword


def create_single_analysis(input_values, config):
    keyword = clean_keyword(input_values['keywords'][0])

    query = create_single_query(keyword, input_values, input_values['limit'])
    database_result = execute_single_analysis_query(query, config, input_values['measure'])

    labels = list(database_result.keys())
    data = [{'y': value[1]['measure'], 'org_y': value[1]['measure']} for value in database_result.values()]

    return labels, [data], [database_result]


def create_contrastive_analysis(input_values, config):
    keywords = list(map(lambda value: clean_keyword(value), input_values['keywords']))
    used_measure = input_values['measure']

    overlap_limit = int(input_values['overlap_limit'] / 100 * input_values['limit'])

    overlap_query = create_overlap_query(keywords[0], keywords[1], input_values)
    overlap = execute_contrastive_analysis_query(overlap_query, config, used_measure)

    global_limit = (input_values['limit'] - min(overlap_limit, len(overlap))) // 2

    results = []
    for k in keywords:
        single_query = create_single_query(k, input_values, global_limit, list(overlap.keys()))
        term = execute_single_analysis_query(single_query, config, used_measure)
        results.append(term)

    overlap = remove_overlap_excess(overlap, overlap_limit)
    labels = list(results[0].keys()) + list(overlap.keys()) + list(results[1].keys())[::-1]

    results = append_overlap(results, overlap)

    measure = list(map(lambda k: k[1]['measure'], chain(results[0].values(), results[1].values())))
    max_value = maximum(measure)
    min_value = minimum(measure)

    data = transform_to_logistic_curve(results, labels, min_value, max_value)

    measure = list(map(lambda k: k['y'], chain(data[0], data[1])))
    max_value_new = maximum(measure)
    min_value_new = minimum(measure)

    offset = int((max_value - abs(min_value)) * 0.03)
    data = rescale(data, min_value, max_value, min_value_new, max_value_new, offset)

    return labels, data, results





