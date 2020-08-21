:- module(a2, [a2/2]).

a2(
	(module{name:Name, exports:Exports}, Clauses),
	module{name:Name, exports:Exports, imports:Imports, body:Body}
):-
	(
		var(Clauses)
	->
		(
			findall(
				Y, 
				(
					member(X, Imports), 
					functor(Y, ':-', 1),
					arg(1, Y, X)
				), 
				Imports2
			),
			append(Imports2, Body, Clauses)		
		)
	;
		(
			partition(is_import, Clauses, Import_Statements, Body),
			findall(Y, (member(X, Import_Statements), arg(1, X.term, Y)), Imports)
		)
	).

is_import(X):-
	functor(X.term, ':-', _),
	arg(1, X.term, Y),
	functor(Y, 'use_module', _).
