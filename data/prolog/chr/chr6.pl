:- use_module(library(chr)).

:- chr_constraint  design_check/0, wire/2, pin_not_checked/1.

design_check, wire(T, U) ==> pin_not_checked(T), pin_not_checked(U).
design_check, pin_not_checked(T) \ pin_not_checked(T) <=> true. % get rid of duplicates
design_check, wire(T, A), wire(T, B) \ pin_not_checked(T) <=> A \= B | true.
design_check, wire(T, A), wire(B, T) \ pin_not_checked(T) <=> A \= B | true.
design_check, wire(A, T), wire(B, T) \ pin_not_checked(T) <=> A \= B | true.
design_check, wire(A, T), wire(T, B) \ pin_not_checked(T) <=> A \= B | true.
design_check \ pin_not_checked(T) <=> format('singleton pin ~q~n', [T]).


to_pairs([I,J|K], [(I-J)|KK]) :-
	to_pairs(K, KK).
to_pairs([], []).

xxx :- 
	to_pairs([0,1,1,2,2,3,3,5,3,0],P),
	maplist([X-Y]>>wire(X,Y), P),
	design_check.
	
:- initialization(xxx).
