:- use_module(library(dcg/basics)).

head(X) --> body(X), end.
body(5) --> [x].
end --> [y].

:- listing(head/3).
:- listing(body/3).
:- listing(end/2).

%test0 :- debug,gtrace,


:- phrase(head(Y), Z),writeq((Y, Z)).

:- set_prolog_flag(double_quotes, codes).
