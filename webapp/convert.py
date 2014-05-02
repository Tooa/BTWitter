'''
Created on 10.01.2014

@author: toa
'''
import sys
import io
import csv
import gzip
from annotator import NameEntityAnnotator, WordClassAnnotator, AnnotationMeta

#TODO: Make chooseble if word convert or rel_s convert so before and after is possible and import 2 files

# Input files
words = sys.argv[1]
co_s = sys.argv[2]
# Output directory
nodes = sys.argv[3]
rel_s = sys.argv[4]
# Relation name
relation = sys.argv[5]

id_to_node = dict()
NameEntityAnnotator('cabaret/upload/multiwords')
WordClassAnnotator('cabaret/upload/postags')

""" Convert to Node file
"""
with io.open(words, 'r') as csv_reader, gzip.open(nodes + '.nodes.gz', "w") as gz_writer:
    reader = csv.reader(csv_reader, delimiter='\t', quotechar='', quoting=csv.QUOTE_NONE)
    writer = csv.writer(io.TextIOWrapper(gz_writer, newline="", write_through=True), delimiter='\t',
                        lineterminator='\n', quotechar='', quoting=csv.QUOTE_NONE)

    #Write header for nodes
    writer.writerow(['identifier:string:TokenNode', 'frequency:int'] + [i.get_type() for i in AnnotationMeta.instances])
    for row in reader:
        #Fix tiny CC error e.g "angela  merkel"
        row[1] = str(row[1]).replace('  ', ' ').replace('\\', '\\\\').replace('\"', '\\\"')
        id_to_node[int(row[0])] = row[1]

        writer.writerow([row[1], row[2]] + [i.get_annotation(row[1]) for i in AnnotationMeta.instances])


with io.open(co_s, 'r') as csv_reader, gzip.open(rel_s + '.relation.gz', "w") as gz_writer:
    reader = csv.reader(csv_reader, delimiter='\t', quotechar='', quoting=csv.QUOTE_NONE)
    writer = csv.writer(io.TextIOWrapper(gz_writer, newline="", write_through=True), delimiter='\t',
                        lineterminator='\n', quotechar='', quoting=csv.QUOTE_NONE)

    #Write header row for relation
    writer.writerow(['identifier:string:TokenNode', 'identifier:string:TokenNode', 'type', 'weight:int', 'll:float', 'lldivnAB:float', 'lldivlognAB:float', 'pmi:float', 'lmi:float'])
    for i, row in enumerate(reader):
        #Note: The relation file is symmetric, so skip every second line
        if (i % 2) == 0:
            continue
        writer.writerow([id_to_node[int(row[0])], id_to_node[int(row[1])], relation, row[2], row[3], row[4], row[5], row[6], row[7]])
