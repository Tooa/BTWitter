import re
from pipeline import CasUtil, Annotation
from componentHelper import emoticon_string, load_name_list, load


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


class StopwordTagger(TokenTagger):
    def __init__(self, list_of_stopwords):
        self._stopwords = load(list_of_stopwords)

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
        self.names = load_name_list(list_of_names)

    def get_token_type(self):
        return "NER"

    def is_token_to_tag(self, token):
        return token.lower() in self.names


