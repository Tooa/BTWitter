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