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

from pipeline import CasUtil, Annotation


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

    @staticmethod
    def is_special_token(c):
        return any([not c.isalpha(), c.startswith("@"), c.startswith("#"), c.startswith("http")])

    def process(self, cas):
        for token_annot in CasUtil.get_annotations(cas, "Token"):
            token = token_annot.get_covered_text()
            normalized = self.normalize_word_token(token)

            if normalized != token:
                norm_annot = Annotation(cas.get_view(), token_annot.begin, token_annot.end, "Error", normalized)
                cas.add_fs_annotation(norm_annot)