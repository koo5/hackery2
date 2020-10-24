:- use_module(library(clpq)).



x :-
	{A = B - W,
	C = Y + X,
	B = Z * C},
	write_term(A, [attributes(write)]).
	