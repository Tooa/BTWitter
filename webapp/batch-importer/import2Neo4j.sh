#!/bin/sh 

# Delete local graph database
rm -R target/graph.db/
# Stop neo4j database service
service neo4j-service stop
# Delete old database
rm -r /var/lib/neo4j/data/graph.db/
# Import data
mvn test-compile exec:java -Dexec.mainClass="org.neo4j.batchimport.Importer" \
  -Dexec.args="batch.properties target/graph.db $1 $2,$3"

# Copy local database to correct dir as neo4j user
su neo4j -c "cp -R target/graph.db/ /var/lib/neo4j/data/"
# Start server again
service neo4j-service start





