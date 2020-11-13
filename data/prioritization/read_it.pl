:- use_module(library(semweb/rdf_db)).
:- use_module(library(semweb/turtle)).  

:- rdf_register_prefix(rdfs,
'http://www.w3.org/2000/01/rdf-schema#').
:- rdf_register_prefix(p, 
'https://koo5.github.io/rdf/prio/').



print_properties_of_edge(E) :-
	findall(_,(
		rdf(E,P,O,_),
		maybe_shorten_uri(P, P2),
		format('^ ~q = ~q ~n', [P2, O])
	),_).


maybe_shorten_uri(Uri, PrefixedUri) :-
	rdf_current_prefix(Namespace_prefix, Namespace),
	string_concat(Namespace,Short_name,Uri),
	atomic_list_concat([Namespace_prefix,':',Short_name], PrefixedUri),
	!.
maybe_shorten_uri(Uri, Uri).


print_maybe_resource_label(X) :-
	(	rdf(X, rdfs:label, Label)
	->	write(Label)
	;	writeq(X)).


print_triple(S,P,O,G) :-
	print_maybe_resource_label(S),
	write(' '),
	maybe_shorten_uri(P,P2),
	write(P2),
	write(' '),
	print_maybe_resource_label(O),
	nl,
	print_properties_of_edge(G),
	nl.


:- 
	Fn = '1.trig',
	rdf_load(Fn,[/*prefixes(Pr),*/base_uri(Fn)]),

	%writeq(Pr),nl,
	%rdf(S,P,O,(G:_Line_number)),
	%writeq((S,P,O,G)),nl,fail,

	rdf_global_id(p:facilitates, P),

	forall(
		rdf(S,P,O,G:_),
		print_triple(S,P,O,G)
	).
	
	