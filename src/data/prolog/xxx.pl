
:- use_module(library(clpfd)).

x :-
	print_term(a, []).

count_ints(i(I), 1) :- I in inf..sup.
count_ints(other(_), 0).