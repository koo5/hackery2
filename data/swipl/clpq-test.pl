:- table exclude2_/3.


:- use_module(library(clpq)).





coord_reduced(coord(Unit, A_Debit, A_Credit), coord(Unit, B_Debit, B_Credit)) :-
	{Common_value = min(A_Debit, A_Credit),
	B_Debit = A_Debit - Common_value,
	B_Credit = A_Credit - Common_value}.


:- meta_predicate
    exclude2(1, +, -).
	
exclude2(Goal, List, Included) :-
    exclude2_(List, Goal, Included).

exclude2_([], _, []).
exclude2_([X1|Xs1], P, Included) :-
    call(P, X1),
    exclude2_(Xs1, P, Included).

exclude2_([X1|Xs1], P, [X1|Included]) :-
    \+call(P, X1),
	exclude2_(Xs1, P, Included).


is_zero(Coord) :-
	is_zero_coord(Coord).
	
is_zero(Value) :-
	is_zero_value(Value).
	
is_zero_coord(coord(_, Zero1, Zero2)) :-
	{Zero1 =:= 0,
	Zero2 =:= 0}.

is_zero_value(value(_, Zero)) :-
	is_zero_coord(coord(_, Zero, 0)).

vec_reduce3([A|As], [B|Bs]) :-
	coord_reduced(A, B),
	vec_reduce3(As, Bs).

vec_reduce3([A|As], [A|Bs]) :-
	A = value(_,_),
	vec_reduce3(As, Bs).


https://www.swi-prolog.org/pldoc/man?section=tabling-status
https://www.swi-prolog.org/pldoc/man?section=tabling-memoize
https://www.swi-prolog.org/pldoc/man?section=tabling-non-termination
https://www.swi-prolog.org/pldoc/doc/_SWI_/library/tabling.pl
https://swi-prolog.discourse.group/t/tabling-meets-negation/411
https://www.google.com/search?q=tabling+with+clp&oq=tabling+with+clp
https://arxiv.org/abs/1809.05771
https://people.eng.unimelb.edu.au/pstuckey/papers/tabled_clp.pdf
https://jorgenavas.github.io/papers/ftclp.pdf
