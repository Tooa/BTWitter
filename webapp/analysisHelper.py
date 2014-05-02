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


def scale(x, origin_max, origin_min, transform_max, transform_min):
    if x == 0:
        return 0
    m = (origin_max - origin_min) / (transform_max - transform_min)
    return m * x + origin_min - m * transform_min


def transform_to_logistic_curve(value, max_v, min_v):
    def logic(x):
        return 0 if x == 0 else -log(1 / x - 1)

    #Note this will maybe return 0 values
    transformed_value = (value - min_v) / max_v
    return {'y': logic(transformed_value), 'org_y': value}