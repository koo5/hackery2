:- use_module(library(semweb/rdf11)).


:- [library(sparqlprog)].
%:- [library('sparqlprog/ontologies/dbpedia')].

:- rdf_register_prefix(dbont,'http://dbpedia.org/ontology/').

x :-

    sparql_endpoint( dbp, 'http://dbpedia.org/sparql/'),
    (dbp ?? rdf(B,rdf:type,dbont:'Band')),
    (dbp ?? rdf(B,dbont:bandMember,M)),
    writeq((B,M)),
    nl,
    false.


:- /*gtrace,*/x.
