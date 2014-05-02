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

