from pipeline import Annotation
from twitterTokenizer import tokenize


class Tokenizer(object):
    def process(self, cas):
        tweet = cas.artifact
        token = tokenize(tweet)

        end = 0
        for t in token:
            start = tweet.find(t, end)
            end = start + len(t) - 1
            annot = Annotation(cas.get_view(), start, end, "Token")
            cas.add_fs_annotation(annot)