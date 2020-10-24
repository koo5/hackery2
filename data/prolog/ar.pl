:- module(ar, []).

:- use_module(library(arithmetic)).


evaluable(T) :- writeln(T), writeln(M).

bobo(X, Y, Z) :- X = Y.

:- A is bobo(7), writeln(A).
