l([_|A], A).



banana("X").


anything([_|A], B) :-
	banana("X").
	anything(A, B).

recu([_|A], B) :-
	recu(A, B).
