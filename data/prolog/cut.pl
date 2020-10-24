a(X) :-
	(
		(
			member(X, [1,2]),
			writeln(X)
		)
	->
		true
	;
		throw(xxx)
	).
	
b :-
	findall(X, a(X), Xs), writeln(Xs).