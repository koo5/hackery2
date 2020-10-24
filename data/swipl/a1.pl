:- module(a1, [a1//2]).

a1(module{name:Name, exports:Exports},Body) --> module_header(Name,Exports), clauses(Body).
module_header(Name,Exports) --> [X],{
	functor(X.term, ':-', _),
	arg(1, X.term, Y),
	functor(Y, 'module', _),
	arg(1, Y, Name),
	arg(2, Y, Exports)
	}.%,m = (:- module(Name,Exports)}.
clauses([]) --> [].
clauses([Head|Body]) --> [Head], clauses(Body).
