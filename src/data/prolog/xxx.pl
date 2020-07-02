
:- use_module(library(clpfd)).

x :-
	print_term(aaaaaaaaaaaa, []).

count_ints(i(I), 1) :- I in inf..sup.
count_ints(other(_), 0).

%:- initialization((x)).
%:- x.
