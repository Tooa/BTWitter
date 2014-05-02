import sys
from os.path import join as joinp

from pipeline import Pipeline
from inputReader import TwitterReader, TopsyReader, RawReader
from tokenizer import Tokenizer
from normalizer import Normalizer
from languageTagger import LanguageTagger
from tokenTagger import CommonTwitterTokenTagger, PunctuationTagger, StopwordTagger, NamedEntityTagger
from casConsumer import DefaultWriter


input_directory = sys.argv[1]
output_directory = sys.argv[2]
corpus = sys.argv[3]

topsy_reader = TopsyReader(joinp(input_directory, "topsy"))
twitter_reader = TwitterReader(joinp(input_directory, "twitter"))
raw_reader = RawReader(joinp(input_directory, "raw"))
lang_tagger = LanguageTagger()
tokenizer = Tokenizer()
normalizer = Normalizer()
ner_tagger = NamedEntityTagger("preprocessor/config/data/multiwordlist")
stopword_tagger = StopwordTagger("preprocessor/config/data/german_stopwords")
punctuation_tagger = PunctuationTagger()
other_tagger = CommonTwitterTokenTagger()
writer = DefaultWriter(output_directory, corpus)

topsy_pipe = Pipeline(topsy_reader, lang_tagger, tokenizer, normalizer, ner_tagger, stopword_tagger, punctuation_tagger,
                      other_tagger, writer)

twitter_pipe = Pipeline(twitter_reader, lang_tagger, tokenizer, normalizer, ner_tagger, stopword_tagger,
                        punctuation_tagger, other_tagger, writer)

counter = twitter_pipe.process()
counter = topsy_pipe.process(counter=counter)