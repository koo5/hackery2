
:- use_module(library(clpfd)).

x :-
	print_term(xxxxxxxxxx, []).
y :-
	print_term(yyyyyyyyyyyyyy, []).
z :-
	print_term(zzzzzzzzzzzzzzzzz, []).

count_ints(i(I), 1) :- I in inf..sup.
count_ints(other(_), 0).

% happens both during compilation and during execution
:- initialization((x)).
% happens during compilation
:- y.



/*

koom@dev ~/hackery2/src/data/prolog (master)> rm a.out* ;swipl -g z -o a.outt -c compilation.pl
yyyyyyyyyyyyyyxxxxxxxxxx⏎
koom@dev ~/hackery2/src/data/prolog (master)> ./a.outt
xxxxxxxxxxzzzzzzzzzzzzzzzzz⏎

*/
