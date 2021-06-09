:- table connection/2.

connection(X, Y) :-
	gensym(c,C),
	format(user_error,'c1a ~q: ~q ~n ',[C,connection(X, Y)]),
        connection(X, X2),
	format(user_error,'c1b ~q: ~q ~n ',[C,connection(X, X2)]),
        connection(X2, Y),
	format(user_error,'c1c ~q: ~q ~n ',[C,connection(X2, Y)]),
		true.

%connection(X, Y) :-
%        connection(Y, X).

connection('Amsterdam', 'Schiphol') :- 
	format(user_error,'c3~n ',[]).
%connection('Amsterdam', 'Haarlem').
connection('Schiphol', 'Leiden') :- 
	format(user_error,'c5~n ',[]).
%connection('Haarlem', 'Leiden').

