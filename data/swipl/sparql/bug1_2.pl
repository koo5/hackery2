#!/usr/bin/env swipl

:- use_module(library(semweb/sparql_client)).
%
:- sparql_query('

select * where {
  ?s ?p ?o.
}
limit 1


', Row,
                [ host('integbio.jp'), path('/rdf/sparql')]),writeq(Row),nl.
