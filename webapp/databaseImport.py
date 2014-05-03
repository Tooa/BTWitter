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

import io
import csv
import gzip
import subprocess
from os import remove
from os.path import join

from annotator import NameEntityAnnotator, WordClassAnnotator, AnnotationMeta

#TODO: Move creation to Annotationmeta with folder and file names
#NameEntityAnnotator('btwitter/upload/multiwordlist.ner')
#WordClassAnnotator('btwitter/upload/postags')


def save_file(file, output_file, allowed_extensions):
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1] in allowed_extensions

    if file and allowed_file(file.filename):
        file.save(output_file)


def convert_nodes(words, nodes_file_name):
    id_to_word = dict()

    with io.open(words, 'r') as csv_reader, gzip.open(nodes_file_name + '.nodes.gz', "w") as gz_writer:
        reader = csv.reader(csv_reader, delimiter='\t', quotechar='', quoting=csv.QUOTE_NONE)
        writer = csv.writer(io.TextIOWrapper(gz_writer, newline="", write_through=True), delimiter='\t',
                            lineterminator='\n', quotechar='', quoting=csv.QUOTE_NONE)

        #Write header for nodes
        writer.writerow(
            ['identifier:string:TokenNode', 'frequency:int'] + [i.get_type() for i in AnnotationMeta.instances])
        for row in reader:
            #Fix tiny CC error e.g "angela  merkel"
            row[1] = str(row[1]).replace('  ', ' ').replace('\\', '\\\\').replace('\"', '\\\"')
            id_to_word[int(row[0])] = row[1]

            writer.writerow([row[1], row[2]] + [i.get_annotation(row[1]) for i in AnnotationMeta.instances])

    return id_to_word


def convert_relation(relation, relation_name, relation_file_name, id_to_word):
    with io.open(relation, 'r') as csv_reader, gzip.open(relation_file_name + '.relation.gz', "w") as gz_writer:
        reader = csv.reader(csv_reader, delimiter='\t', quotechar='', quoting=csv.QUOTE_NONE)
        writer = csv.writer(io.TextIOWrapper(gz_writer, newline="", write_through=True), delimiter='\t',
                            lineterminator='\n', quotechar='', quoting=csv.QUOTE_NONE)

        #Write header row for relation
        writer.writerow(['identifier:string:TokenNode', 'identifier:string:TokenNode', 'type', 'weight:int', 'll:float',
                         'lldivnAB:float', 'lldivlognAB:float', 'pmi:float', 'lmi:float'])

        for i, row in enumerate(reader):
            #Note: The relation file is symmetric, so skip every second line
            if (i % 2) == 0:
                continue
            writer.writerow(
                [id_to_word[int(row[0])], id_to_word[int(row[1])], relation_name, row[2], row[3], row[4], row[5],
                 row[6], row[7]])


def do_import(request, upload_folder):
    files_to_store = ['before_words', 'before_rel', 'after_words', 'after_rel', 'postags', 'multiwordlist.ner']

    for i, file in zip(range(1, 7), files_to_store):
        save_file(request.files['file' + i], join(upload_folder, file))

    corpus_before_name = 'corpus_before'
    corpus_after_name = 'corpus_after'

    #Convert corpus before
    id_to_word = convert_nodes(join(upload_folder, files_to_store[0]), join(upload_folder, corpus_before_name))
    convert_relation(join(upload_folder, files_to_store[1]), 'BEFORE', join(upload_folder, corpus_before_name),
                     id_to_word)
    #Convert corpus after
    id_to_word = convert_nodes(join(upload_folder, files_to_store[2]), join(upload_folder, corpus_after_name))
    convert_relation(join(upload_folder, files_to_store[3]), 'AFTER', join(upload_folder, corpus_after_name),
                     id_to_word)

    for file in files_to_store:
        remove(join(upload_folder, file))

    subprocess.call(
        ['batch-importer/import2Neo4j.sh',
         join(upload_folder, corpus_after_name + '.nodes.gz'),
         join(upload_folder, corpus_after_name + '.relation.gz'),
         join(upload_folder, corpus_before_name + '.relation.gz')])
