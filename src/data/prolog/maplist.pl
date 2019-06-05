transform(DOM, In, Out) :-
   Out is In + DOM.

:- maplist(transform(10), [1,2,3], L), print_term(L, []).