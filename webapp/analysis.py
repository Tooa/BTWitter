from itertools import chain

from analysisQuery import create_single_query, create_overlap_query, execute_single_analysis_query, \
    execute_contrastive_analysis_query
from analysisHelper import transform_to_logistic_curve, rescale, remove_overlap_excess, append_overlap
from requestHelper import clean_keyword


def create_single_analysis(input_values, config):
    keyword = clean_keyword(input_values['keywords'][0])

    query = create_single_query(keyword, input_values, input_values['limit'])
    database_result = execute_single_analysis_query(query, config, input_values['measure'])

    labels = list(database_result.keys())
    data = list(map(lambda value: value[1]['measure'], database_result.values()))

    return labels, data, [database_result]


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

    max_value = max(chain(results[0].values(), results[1].values()), key=lambda k: k[1]['measure'])[1]['measure']
    min_value = min(chain(results[0].values(), results[1].values()), key=lambda k: k[1]['measure'])[1]['measure']

    data = transform_to_logistic_curve(results, labels, min_value, max_value)

    max_value_new = max(chain(data[0], data[1]), key=lambda k: k['y'])['y']
    min_value_new = min(chain(data[0], data[1]), key=lambda k: k['y'])['y']

    offset = int((max_value - abs(min_value)) * 0.03)
    data = rescale(data, min_value, max_value, min_value_new, max_value_new, offset)

    return labels, data, results





