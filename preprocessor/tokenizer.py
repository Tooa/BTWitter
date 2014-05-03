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