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
		maybe_shorten(O, O2),
		format('^ ~q = ~q ~n', [P2, O2])
	),_).


maybe_shorten_uri(Uri, PrefixedUri) :-
	shorten_uri(Uri, PrefixedUri), !.
maybe_shorten_uri(Uri, Uri) :- !.

shorten_uri(Uri, PrefixedUri) :-
	atomic(Uri),
	rdf_current_prefix(Namespace_prefix, Namespace),
	string_concat(Namespace,Short_name,Uri),
	atomic_list_concat([Namespace_prefix,':',Short_name], PrefixedUri),
	!.

maybe_shorten_literal(L, L2) :- 
	shorten_literal(L, L2),!.

maybe_shorten_literal(X,X) :- !.

shorten_literal(literal(type(_,L2)), L2) :- !.
shorten_literal(literal(L2), L2) :- !.


maybe_shorten(X,Y) :-
	shorten_literal(X,Y),!.
maybe_shorten(X,Y) :-
	shorten_uri(X,Y),!.
maybe_shorten(X,X) :- !.


print_maybe_resource_label(X) :-
	(	rdf(X, rdfs:label, Label)
	->	Y = Label
	;	Y = X),
	maybe_shorten(Y, Y2),
	writeq(Y2).


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
	
	
