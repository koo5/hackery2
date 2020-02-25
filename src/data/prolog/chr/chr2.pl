:- use_module(library(chr)).





:- chr_constraint generate/1, value/1.
generate(1) <=> true.
generate(N) <=> N > 1 | value(N),
M is N - 1, generate(M).
value(I) \ value(J) <=> J mod I =:= 0 | true.





:- chr_constraint coin/0, heads/0, tails/0.
coin ==> heads.
coin ==> tails.





:- chr_constraint domain/1.
domain(X) <=> X = 5.

:- chr_constraint domain/2.
domain(X,[V]) <=> X = V.






