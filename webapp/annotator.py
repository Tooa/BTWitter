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

import io
from collections import defaultdict, Counter


class AnnotationMeta(type):
    instances = []

    def __new__(metacls, name, bases, dct):
        if name != "Annotation" and ("get_type" not in dct or "get_annotation" not in dct):
            raise TypeError("Annotation needs get_type and get_annotation")

        return super(AnnotationMeta, metacls).__new__(metacls, name, bases, dct)

    def __call__(cls, *args, **kw):
        i = super(AnnotationMeta, cls).__call__(*args, **kw)
        AnnotationMeta.instances.append(i)

        return i


class Annotation(object, metaclass=AnnotationMeta):
    def __init__(self, file):
        """ Executes itself in the given environment.
        """
        pass


class NameEntityAnnotator(Annotation):
    def __init__(self, file):
        self._name_list = self._load_name_list(file)

    def _load_name_list(self, file):
        l = []
        with io.open(file, 'r', encoding='utf-8') as f:
            for line in f:
                name = line.replace('\n', '')
                #Add partial word and the entire one
                l += name.split() + [name]
        return l

    def get_type(self):
        return 'name_entity:int'

    def get_annotation(self, token):
        return 1 if token in self._name_list else 0


class WordClassAnnotator(Annotation):
    def __init__(self, file):
        self._word_classes = self._chose_most_common_number(self._read_word_class_file(file))

    def _chose_most_common_number(self, dic):
        def most_common(counter):
            return counter.most_common(1)[0][0]

        for key in dic.keys():
            dic[key] = most_common(dic[key])
        return dic

    def _read_word_class_file(self, file):
        word_classes = defaultdict(Counter)
        with io.open(file, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                l = []
                [l.append(tuple(w.rsplit('|', 1))) for w in line.split()]

                for t in l:
                    word_classes[t[0].lower()].update({t[1].replace('*', ''): 1})
        return word_classes

    def get_type(self):
        return 'word_class:int'

    def get_annotation(self, token):
        if token.startswith('@'):
            return -2
        elif token.startswith('#'):
            return -1
        elif self._word_classes[token]:
            return self._word_classes[token]
        else:
            return 0


