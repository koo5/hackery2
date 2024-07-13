
from rdflib_neo4j import Neo4jStoreConfig, Neo4jStore, HANDLE_VOCAB_URI_STRATEGY
from rdflib import Graph

import os

auth_data = {'uri': os.environ['AURA_DB_URI'],
             'database':"neo4j",
             'user':'neo4j',
             'pwd':os.environ['AURA_DB_PWD']}

# Define your custom mappings & store config
config = Neo4jStoreConfig(auth_data=auth_data,
                          custom_prefixes=[],
                          handle_vocab_uri_strategy=HANDLE_VOCAB_URI_STRATEGY.IGNORE,
                          batching=True)
                          
                          
file_path = 'http://jj.internal:8877/tmp/last_result/000000_doc_final.turtle'



neo4j_aura = Graph(store=Neo4jStore(config=config))
neo4j_aura.parse(file_path, format="ttl")
neo4j_aura.close(True)


