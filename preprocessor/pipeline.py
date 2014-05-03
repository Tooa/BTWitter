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

from componentHelper import vowel_dic, multiple_replace


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


