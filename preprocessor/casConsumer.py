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
import re
import csv
from collections import defaultdict
from os.path import join as joinp

from pipeline import CasUtil
from componentHelper import emoticon_string, load


class DefaultWriter(object):
    def __init__(self, dir, corpus_name):

        self.dir = dir
        self.corpus_name = corpus_name
        self.unique_token = defaultdict(int)

        self.f_token = open(joinp(self.dir, self.corpus_name + ".tok"), 'a')
        self.token_writer = csv.writer(self.f_token, delimiter='\t', lineterminator='\n', quotechar='',
                                       quoting=csv.QUOTE_NONE)

        self.f_raw_token = open(joinp(self.dir, self.corpus_name + ".raw_token"), 'a')
        self.raw_token_writer = csv.writer(self.f_raw_token, delimiter='\t', lineterminator='\n', quotechar='',
                                           quoting=csv.QUOTE_NONE)

        self.f_sent = open(joinp(self.dir, self.corpus_name + ".sentences"), 'a')
        self.sent_writer = csv.writer(self.f_sent, delimiter='\t', lineterminator='\n', quotechar='',
                                      quoting=csv.QUOTE_NONE)

        self.emoticon_re = re.compile(emoticon_string, re.VERBOSE | re.I | re.UNICODE)
        # TODO: use path from config or cmdline
        self.standard_abbreviations = load('preprocessor/config/data/abbrev')

    #TODO move to helper and rename to lower_token_if_not_smiley
    def lower_token(self, token):
        return token if self.emoticon_re.search(
            token) or token.lower() in self.standard_abbreviations else token.lower()

    def process(self, cas):
        lang = next(CasUtil.get_annotations(cas, "Language"))

        if lang.value != "de":
            return

        filtered_token = []
        for annot in CasUtil.get_all_annotations(cas):
            self.add_to_filtered_token(annot, filtered_token)

        for t in filtered_token:
            self.unique_token[t.lower()] = 1 if CasUtil.has_annotation(cas, t, 'NER') else 0

        self.write_output_files(cas, filtered_token)

    def on_exit(self):
        #Write Ner File
        with io.open(joinp(self.dir, self.corpus_name + ".ner"), 'w', encoding="utf-8") as f:
            ner_writer = csv.writer(f, delimiter='\t', lineterminator='\n', quotechar='',
                                    quoting=csv.QUOTE_NONE)
            for token, ner in self.unique_token.items():
                ner_writer.writerow([token, ner])

                #TODO Using Two pipes will bring error because stream is closed after first
                #self.f_sent.close()
                #self.f_token.close()
                #self.f_raw_token.close()

    def add_to_filtered_token(self, annot, filtered_token):
        token = self.lower_token(annot.get_covered_text())
        if annot.type == "Stopword" or annot.type == "Punctuation" or annot.type == "CommonTwitterToken":
            if token in filtered_token:
                filtered_token.remove(token)
        elif annot.type == "Error":
            index = filtered_token.index(token)
            filtered_token[index] = annot.value.lower()
        elif annot.type == "Token":
            filtered_token.append(token)

    def write_output_files(self, cas, filtered_token):
        self.sent_writer.writerow([cas.document_id, cas.date, cas.artifact])
        self.token_writer.writerow([cas.document_id, cas.date, " ".join(filtered_token)])

        raw_token = [annot.get_covered_text() for annot in CasUtil.get_annotations(cas, "Token")]
        self.raw_token_writer.writerow([" ".join(raw_token)])


class ConsoleWriter(object):
    def process(self, cas):
        print("Artifact:", cas.artifact)
        for annot in CasUtil.get_all_annotations(cas):
            print(annot, annot.get_covered_text())


class StandoffMarkupWriter(object):
    def __init__(self, dir, corpus_name):
        self.dir = dir
        self.corpus_name = corpus_name

        self.f = open(joinp(self.dir, self.corpus_name + ".standoff"), 'a')

    def process(self, cas):
        self.f.write('<document id=' + str(cas.document_id) + '>\n')
        self.f.write('\t<text>' + cas.artifact + '</text>\n')
        self.f.write('\t<annotations>\n')
        for annot in CasUtil.get_all_annotations(cas):
            xml = '\t\t<annotation'
            xml += ' begin=' + str(annot.begin)
            xml += ' end=' + str(annot.end)
            xml += ' type=' + annot.type if annot.type else ''
            xml += ' value=' + str(annot.value) if annot.value else ''
            xml += ' />\n'
            self.f.write(xml)
        self.f.write('\t</annotations>\n')
        self.f.write('</document>\n\n')

    def on_exit(self):
        self.f.close()