call_with_string_read_stream(String, Callable) :-
	setup_call_cleanup(
		new_memory_file(X),
		(
			open_memory_file(X, write, W),
			write(W, String),
			close(W),
			open_memory_file(X, read, R),
			call(Callable, R),
			close(R)),
		free_memory_file(X)).


x :-
	push_operators([op(900,fx,$>)]),
	call_with_string_read_stream("x :- $>x.\n y :- $>11.", hhh),
	true
	,pop_operators
	.
	
hhh(Stream) :-
	read_clause(Stream, Term, []),
	writeq(Term),nl,
	read_term(Stream, Term2, []),
	writeq(Term2),nl.
	

							  
