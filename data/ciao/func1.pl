:- module(_, _, [functional , lazy]).

nrev([]) := [].
nrev([H|T]) := ~conc(nrev(T), [H]).

conc([], L) := L.
conc([H|T], K) := [H | conc(T, K)].

fact(N) := N=0 ? 1
         | N>0 ? N * fact(--N).

:- lazy fun_eval nums_from/1.
nums_from(X) := [X | nums_from(X+1)].

:- use_module(library('lazy/lazy_lib'), [take/3]).

nums(N) := ~take(N, nums_from(0)).
