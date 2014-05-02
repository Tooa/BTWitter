'''
Created on 10.01.2014

@author: toa
'''

import io
from collections import defaultdict, Counter


class Annotation:
    def __init__(self, file):
        """ Executes itself in the given environment.
        """
        pass
    def get_type(self):
        """ Executes itself in the given environment.
        """
        pass

    def get_annotation(self, token):
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



class Annotator:
    # TODO: Do this with *classes arguments "Name-enity-annotator" and generate a list of them according to the string
    def __init__(self, *classes):
        self._annotators = []
        self._name_entity_annotator = NameEntityAnnotator('python/multiwordlist')
        self._word_class_annotator = WordClassAnnotator('python/output.postags')

    def _create(self, annotator_name):
        if annotator_name == 'NameEntityAnnotator':
            cls = NameEntityAnnotator
        #else
        #    cls = ..
        return cls('python/multiwordlist')


    def get_annotation_type(self):
        return [self._name_entity_annotator.get_type(), self._word_class_annotator.get_type()]

    def get_annotations(self, token):
        return [self._name_entity_annotator.get_annotation(token), self._word_class_annotator.get_annotation(token)]
