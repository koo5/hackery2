:- use_module(library(chr)).


/*
one-way unification
only instantiates (rule) head
does not instantiate (stored) constraints
*/

:- chr_constraint c/1.
c(world) <=> writeln('Hello, World!').

?- c(X).
c(X).

?- c(world).
Hello, World!
true.

/*
but prolog in body can
*/

:- chr_constraint domain/1.
domain(X) <=> X = 5.



% =========



:- chr_constraint value/1.
%value(I), value(J) <=> append([I],[J],K), value(K).
%value(O) <=> append(O,O,OO) | banana(OO).
value(1), value(2) <=> value(mkkk).



