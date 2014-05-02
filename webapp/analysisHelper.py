from math import log
from collections import OrderedDict


def remove_overlap_excess(overlap, limit):
    tmp = OrderedDict()
    for i, t in enumerate(overlap.items()):
        if i >= limit:
            break
        k, v = t
        tmp[k] = v

    return tmp


def append_overlap(single_results, overlap):
    tmp = OrderedDict()
    for k, v in overlap.items():
        single_results[0][k] = (v[0], v[1])
        tmp[k] = (v[0], v[2])

    for k, v in single_results[1].items():
        tmp[k] = (v[0], v[1])

    single_results[1] = tmp

    return single_results


def rescale(data, min_value, max_value, min_value_new, max_value_new, offset):
    tmp1 = [
        {'y': max(scale(d['y'], max_value, min_value, max_value_new, min_value_new), offset), 'org_y': d['org_y']}
        if d['org_y'] != 0 else {'y': 0, 'org_y': 0} for d in data[0]]
    tmp2 = [{'y': max(scale(d['y'], max_value, min_value, max_value_new, min_value_new), offset) * -1,
             'org_y': d['org_y']}
            if d['org_y'] != 0 else {'y': 0, 'org_y': 0} for d in data[1]]

    return [tmp1, tmp2]


def scale(x, origin_max, origin_min, transform_max, transform_min):
    if x == 0:
        return 0
    m = (origin_max - origin_min) / (transform_max - transform_min)
    return m * x + origin_min - m * transform_min


def logic(x):
    return 0 if x == 0 else -log(1 / x - 1)


def transform_data_point(value, min_v, max_v):
    #Note this will maybe return 0 values
    transformed_value = (value - min_v) / max_v
    return {'y': logic(transformed_value), 'org_y': value}


def transform_to_logistic_curve(data, labels, min_v, max_v):
    transformed = [
        [transform_data_point(data[0].get(t)[1]['measure'], min_v, max_v)
         if t in data[0] else {'y': 0, 'org_y': 0} for t in labels],
        [transform_data_point(data[1].get(t)[1]['measure'], min_v, max_v)
         if t in data[1] else {'y': 0, 'org_y': 0} for t in labels]
    ]

    return transformed
