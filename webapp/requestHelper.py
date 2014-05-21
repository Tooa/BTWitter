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

import re
from json import loads
from itertools import chain


vowel_dic = {'ä': 'ae', 'Ä': 'ae', 'ü': 'ue', 'Ü': 'ue', 'Ö': 'oe', 'ö': 'oe', 'ß': 'ss', 'ẞ': 'ss'}

pos_dict = {'verben': True, 'usernamen': True, 'standorte': True, 'sonstige': True, 'nomen': True, 'adjektive': True,
            'hashtags': True}


merkel_steinbrueck = {'Number': '1', 'P1': 'Angela Merkel', 'P2': 'Peer Steinbrück',
                                 'Description': 'Kontrastive Kollokationsanalyse zwischen Angela Merkel und Peer Steinbrück. Betrachtet werden 40 Begriffe.',
                                 'K1': 'merkel', 'K2': 'steinbrück', 'overlap_limit': 25,
                                 'pos': pos_dict,
                                 'opts': {'include': True, 'only_names': False}}

merkel_steinbrueck_adjectives = {'Number': '2', 'P1': 'Angela Merkel', 'P2': 'Peer Steinbrück',
                                 'Description': 'Eine auf Adjektive beschränkte Analyse mit einem Schnitt von mindestens 50 Prozent',
                                 'K1': 'merkel', 'K2': 'steinbrück', 'overlap_limit': 50,
                                 'pos': {k: v if k == 'adjektive' else not v for (k, v) in pos_dict.items()},
                                 'opts': {'include': True, 'only_names': False}}

ramsauer_mainz = {'Number': '1', 'P1': 'Peter Ramsauer', 'P2': 'Deutsche Bahn',
                                 'Description': 'Kontrastive Kollokationsanalyse zwischen Peter Ramsauer und der deutschen Bahn',
                                 'K1': 'ramsauer', 'K2': 'bahn', 'overlap_limit': 50,
                                 'pos': pos_dict,
                                 'opts': {'include': True, 'only_names': False}}


examples = [merkel_steinbrueck, merkel_steinbrueck_adjectives, ramsauer_mainz]


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


def multiple_replace(text, dic):
    # Note this implementation uses a single pass and ignores letter case!
    regex = re.compile(r"|".join(map(re.escape, list(dic.keys()))))
    return regex.sub(lambda mo: dic[mo.group(0)], text)


def clean_keyword(keyword):
    return multiple_replace(keyword.lower(), vowel_dic).lstrip()

