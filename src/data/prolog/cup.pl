a(Xs) :-
	findall(
		X,
		(
			(
				member(X, [1,2,3])
			->
				print_term(X, [])
			;
				print_term(z, [])
			)
		),
		Xs
	).