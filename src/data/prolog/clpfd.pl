

:- use_module(library(clpfd)).
:- use_module(library(clpq)).

list_length([], 0).
list_length([_|Ls], Length) :-
	Length #> 0,
	Length #= Length0 + 1,
	list_length(Ls, Length0).

list_lengthq([], 0).
list_lengthq([_|Ls], Length) :-
	{Length > 0,
	Length = Length0 + 1},
	list_lengthq(Ls, Length0).
	    