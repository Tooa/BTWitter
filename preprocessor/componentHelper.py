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
import io


def load(filename):
    # TODO: Test f.readlines()
    data = []
    with io.open(filename, 'rU', encoding='utf-8') as f:
        for line in f:
            data.append(line.replace('\n', ''))
    return data


def load_name_list(file):
        l = []
        with io.open(file, 'r', encoding='utf-8') as f:
            for line in f:
                name = line.replace('\n', '')
                #Add partial word and the entire one
                l += name.split(maxsplit=1) + [name]
        return l


def multiple_replace(text, dic):
        # Note this implementation uses a single pass and ignores letter case!
        regex = re.compile(r"|".join(map(re.escape, list(dic.keys()))))
        return regex.sub(lambda mo: dic[mo.group(0)], text)


vowel_dic = {'ä': 'ae', 'Ä': 'ae', 'ü': 'ue', 'Ü': 'ue', 'Ö': 'oe', 'ö': 'oe', 'ß': 'ss', 'ẞ': 'ss'}

emoticon_string = r"""
        (?:
          [<>]?
          [:;=8]                     # eyes
          [\-o\*\']?                 # optional nose
          [\)\]\(\[dDpP/\:\}\{@\|\\] # mouth
          |
          [\)\]\(\[dDpP/\:\}\{@\|\\] # mouth
          [\-o\*\']?                 # optional nose
          [:;=8]                     # eyes
          [<>]?
        )"""

