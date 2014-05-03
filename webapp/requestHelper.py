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

