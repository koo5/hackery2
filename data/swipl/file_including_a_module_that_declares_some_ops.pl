%:- [module_declaring_some_ops].
:- use_module(module_declaring_some_ops, [m/0]).
%:- use_module([module_declaring_some_ops, ops_module]).
%:- use_module(module_declaring_some_ops, all).

x :-
	?(!(x)).
	
%y :-
%	*y.


