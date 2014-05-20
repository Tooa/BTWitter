#!/bin/sh

# sudo su postgres
# createuser tiny
# createdb corpus
# psql 
# alter user tiny with encrypted password 'tiny';
# grant all privileges on database corpus to tiny;

# sudo -u postgres psql damit einloggen als superuser
# \c database_name connect to database

# $1 == psql user
# $2 == psql db
# $3 == psql pass
# $4 == words file
# $5 == sentences file
# $6 == word-sentence index

export PGPASSWORD=$3

psql="psql -h localhost -U $1 -d $2"

$psql --c "drop table words cascade;"
$psql --c "drop table sentences cascade;"
$psql --c "drop table inv_w cascade;"

$psql --c "create table words (id integer, word text, freq integer, primary key(id));"
$psql --c "create table sentences (id integer, sentence text, primary key(id));"
$psql --c "create table inv_w (wordId integer references words(id), 
															sentenceId integer references sentences(id), 
															position integer, 
															foreign key(wordId) references words(id), 
															foreign key(sentenceId) references sentences(id));"

#Remove last column from file
cut -f1,2,3 $6 > $6.clean
#Escape backslash in words file
#perl -p -i -e 's/\\/\\\\/g;' $4
#Escape backslash in sentences file
#perl -p -i -e 's/\\/\\\\/g;' $5

$psql --c "\copy words from '$4';" 
$psql --c "\copy sentences from '$5';"
$psql --c "\copy inv_w from '$6.clean';"

$psql --c "CREATE INDEX idx_index_wordId ON inv_w USING btree (wordId);"
$psql --c "CREATE INDEX idx_index_sentenceId ON inv_w USING btree (sentenceId);"
$psql --c "CREATE INDEX idx_index_wordId_sentenceId ON inv_w USING btree (wordId, sentenceId);"

rm $6.clean
