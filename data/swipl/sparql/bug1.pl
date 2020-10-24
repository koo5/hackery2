#!/usr/bin/env swipl

/*

WARNING: you must edit /usr/local/lib/swipl/library/semweb/sparql_client.pl (or wherever it is on your system) and make sure that application/sparql-results+json goes before xml. Otherwise, agraph sends back xml, and sparql_client.pl sparql_read_xml_result/2 has "space(remove)", which removes whitespace (including newlines) from literals. See also https://github.com/SWI-Prolog/packages-semweb/issues/91 .

*/

% swipl -g "pack_install('https://github.com/cmungall/sparqlprog.git')."
:- [library(sparqlprog)].

main :-
	debug(sparqlprog),

    /*
	sparql_endpoint( l, 'http://192.168.123.10:10035/repositories/repo/'),
	findall(_,
	(
        (l ?? rdf(S, P, O, Graph)),
        writeq(O),
        nl
    ),_),
    */


    sparql_endpoint( r, 'https://integbio.jp/rdf/sparql'),
	(r ?? rdf(S, P, O, Graph)),
    nl.
