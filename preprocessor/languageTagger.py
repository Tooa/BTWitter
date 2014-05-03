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
from language_filter.ldig import ldig


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

