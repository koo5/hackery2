:- use_module(library(semweb/sparql_client)).
%
:- sparql_query('

select distinct ?o where {
  <http://dbpedia.org/ontology/> rdfs:comment ?o.
}
limit 1


', Row,
                [ host('dbpedia.org'), path('/sparql/')]),writeq(Row),nl.
