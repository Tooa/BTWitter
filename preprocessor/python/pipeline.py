import re
import io
import csv
import sys
from datetime import datetime
from os.path import join as joinp
from collections import defaultdict
from processing.twitterTokenizer import tokenize
from pipeline_helper import emoticon_string, load, load_name_list, vowel_dic, multiple_replace
from inputReader import TopsyReader, TwitterReader, RawReader
from language_filter.ldig import ldig


class Cas(object):
    def __init__(self, date, artifact, id):
        self.views = {"Default": View(self, artifact)}
        self.date = date
        self.document_id = id

    @property
    def artifact(self):
        return self.views["Default"].artifact

    def add_view(self, key, artifact):
        self.views[key] = View(self, artifact)

    def get_view(self, key="Default"):
        return self.views[key] if key in self.views else self.views["Default"]

    def add_fs_annotation(self, annot):
        return self.views["Default"].add_fs_annotation(annot)


class CasUtil(object):
    @staticmethod
    def get_all_annotations(cas):
        for v in cas.views.values():
            for a in v.annotations:
                yield a

    @staticmethod
    def get_annotations(cas, type):
        for v in cas.views.values():
            for a in v.get_annotations_by_type(type):
                yield a

    @staticmethod
    def has_annotation(cas, text, type):
        for annot in CasUtil.get_annotations(cas, type):
            covered_text = annot.get_covered_text()
            if covered_text.lower() == text.lower():
                return True
        return False


class View(object):
    def __init__(self, cas, artifact):
        self.cas = cas
        self.artifact = artifact
        self.annotations = []

    def add_fs_annotation(self, annot):
        self.annotations.append(annot)

    def get_annotations_by_type(self, typ):
        return list(filter(lambda x: x.type == typ, self.annotations))


class Annotation(object):
    def __init__(self, view, begin, end, type, value=None):
        self.artifact = view.artifact
        self.begin = begin
        self.end = end
        self.type = type
        self.value = value

    def get_covered_text(self):
        return self.artifact[self.begin:self.end + 1]

    def __str__(self):
        return """{}({}, {}, value={})""".format(self.type, self.begin, self.end, self.value)

    def __repr__(self):
        return str(self)


class Pipeline(object):
    def __init__(self, *modules):
        self.modules = modules[1:]
        self.reader = modules[0]

    def process(self, counter=0):

        for m in self.modules:
            if hasattr(m, "on_init"):
                m.on_init()

        for date, text in self.reader.stream():
            text = multiple_replace(text, vowel_dic)
            counter += 1
            cas = Cas(date, text, counter)

            for m in self.modules:
                m.process(cas)

        for m in self.modules:
            if hasattr(m, "on_exit"):
                m.on_exit()

        return counter


class Tokenizer(object):
    def process(self, cas):
        tweet = cas.artifact
        # Assume that the tweet is already unescaped (see input reader)
        token = tokenize(tweet)
        end = 0
        for t in token:
            start = tweet.find(t, end)
            end = start + len(t) - 1
            annot = Annotation(cas.get_view(), start, end, "Token")
            cas.add_fs_annotation(annot)


class LanguageTagger(object):
    def __init__(self):
        self._detector = ldig('preprocessor/python/language_filter/models/model.latin')

    def process(self, cas):
        view = cas.get_view()
        text = view.artifact
        # check if case sensitive
        lang = self._detector.detect_language(text)
        lang_annot = Annotation(view, 0, len(text), "Language", lang)
        cas.add_fs_annotation(lang_annot)


class Normalizer(object):
    def normalize_word_token(self, token):
        # TODO: lOoOoOoOoOoOoOoOoOoOoOoOoOoOoOoOol does not work
        tout = ""
        num_consec = 0
        last_char = None

        if self.is_special_token(token):
            return token

        for c in token:
            num_consec = num_consec + 1 if c == last_char else 0

            if num_consec >= 2:
                continue

            tout += c
            last_char = c
        return tout

    def is_special_token(c):
        return any([not c.isalpha(), c.startswith("@"), c.startswith("#"), c.startswith("http")])

    def process(self, cas):
        # TODO: Read tokens from all views, add new annotations to default view??! wtf?!
        for token_annot in CasUtil.get_annotations(cas, "Token"):
            token = token_annot.get_covered_text()
            normalized = self.normalize_word_token(token)

            if normalized != token:
                # duplicate annotation
                norm_annot = Annotation(cas.get_view(), token_annot.begin, token_annot.end, "Error", normalized)
                cas.add_fs_annotation(norm_annot)


class TokenTagger(object):
    def get_token_type(self):
        pass

    def is_token_to_tag(self, token):
        pass

    def process(self, cas):
        for token_annot in CasUtil.get_annotations(cas, "Token"):
            token = token_annot.get_covered_text()
            if self.is_token_to_tag(token):
                annot = Annotation(cas.get_view(), token_annot.begin, token_annot.end, self.get_token_type())
                cas.add_fs_annotation(annot)


#TODO Achtung immer auf die Umlaute in der Stopword list achten.
class StopwordTagger(TokenTagger):
    def __init__(self, list_of_stopwords):
        self._stopwords = list_of_stopwords

    def get_token_type(self):
        return "Stopword"

    def is_token_to_tag(self, token):
        return token.lower() in self._stopwords


class PunctuationTagger(TokenTagger):
    def __init__(self):
        self.emoticon_re = re.compile(emoticon_string, re.VERBOSE | re.I | re.UNICODE)

    #THis regex suckes because appendix
    def contains_letter_or_number(self, token):
        return bool(re.search('[a-zA-Z\döüäßẞà]+', token))

    def get_token_type(self):
        return "Punctuation"

    def is_token_to_tag(self, token):
        return not (self.contains_letter_or_number(token.lower()) or self.emoticon_re.search(token.lower()))


class CommonTwitterTokenTagger(TokenTagger):
    def get_token_type(self):
        return "CommonTwitterToken"

    def is_token_to_tag(self, token):
        return token.lower().startswith("http") or "rt" == token.lower() or (token.isalpha() and len(set(token)) == 1)


class NamedEntityTagger(TokenTagger):
    def __init__(self, list_of_names):
        self.names = list_of_names

    def get_token_type(self):
        return "NER"

    def is_token_to_tag(self, token):
        return token.lower() in self.names


class CasConsumer(object):
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

        #Store NER
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


class CasConsoleLogger(object):
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


class CasSentenceWriterForBTW(object):
    def __init__(self, dir, corpus_name):
        self.dir = dir
        self.corpus_name = corpus_name

        self.f_sent_before = open(joinp(self.dir, self.corpus_name + ".before.sentences"), 'a')
        self.sent_writer_before = csv.writer(self.f_sent_before, delimiter='\t', lineterminator='\n', quotechar='',
                                             quoting=csv.QUOTE_NONE)

        self.f_sent_after = open(joinp(self.dir, self.corpus_name + ".after.sentences"), 'a')
        self.sent_writer_after = csv.writer(self.f_sent_after, delimiter='\t', lineterminator='\n', quotechar='',
                                            quoting=csv.QUOTE_NONE)

    def process(self, cas):
        if cas.date > datetime(2013, 9, 22).date():
            self.sent_writer_after.writerow([cas.date, cas.artifact])
        else:
            self.sent_writer_before.writerow([cas.date, cas.artifact])

    def on_exit(self):
        self.f_sent_after.close()
        self.f_sent_before.close()



input_directory = sys.argv[1]
output_directory = sys.argv[2]
corpus = sys.argv[3]

topsy_reader = TopsyReader(joinp(input_directory, "topsy"))
twitter_reader = TwitterReader(joinp(input_directory, "twitter"))
raw_reader = RawReader(joinp(input_directory, "raw"))
#lang_tagger = LanguageTagger()
tokenizer = Tokenizer()
#normalizer = Normalizer()
#ner_tagger = NamedEntityTagger(load_name_list("preprocessor/config/data/multiwordlist"))
#stopword_tagger = StopwordTagger(load("preprocessor/config/data/german_stopwords"))
#punctuation_tagger = PunctuationTagger()
#other_tagger = CommonTwitterTokenTagger()
#writer = CasConsumer(output_directory, corpus)

raw_writer = CasSentenceWriterForBTW(output_directory, corpus)
standoff_writer = StandoffMarkupWriter(output_directory, corpus)

#raw_pipe = Pipeline(raw_reader, raw_writer)
twitter_pipe = Pipeline(twitter_reader, raw_writer)
topsy_pipe = Pipeline(topsy_reader, raw_writer)


counter = twitter_pipe.process()
print(counter)
counter = topsy_pipe.process(counter=counter)
#raw_pipe.process()




#TODO list argument
#topsy_pipe = Pipeline(topsy_reader, lang_tagger, tokenizer, normalizer, ner_tagger, stopword_tagger, punctuation_tagger,
#                      other_tagger, writer)

#twitter_pipe = Pipeline(twitter_reader, lang_tagger, tokenizer, normalizer, ner_tagger, stopword_tagger,
#                        punctuation_tagger, other_tagger, writer)

#counter = twitter_pipe.process()
#print(counter)
#counter = topsy_pipe.process(counter=counter)
