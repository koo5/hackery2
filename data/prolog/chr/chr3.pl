:- use_module(library(chr)).

:- chr_constraint domain/2, indomain/1.

domain(X,L) <=> ground(X) | memberchk(X,L).
domain(_,[]) <=> fail.
domain(X,[V]) <=> X = V.
domain(X,L1), domain(X,L2) <=> intersection(L1,L2,L), domain(X,L).
indomain(X) <=> ground(X) | true.
indomain(X), domain(X,Vs) <=> member(X,Vs).








