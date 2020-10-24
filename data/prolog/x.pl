% https://en.wikipedia.org/wiki/Backus%E2%80%93Naur_form#Introduction


use_module(library(dcg/basics)). 


symbol --> symbol_char, maybe_more_symbol_chars.
maybe_more_symbol_chars --> (symbol_char; []).
symbol_char --> [[X]], {is_symbol_char(X)}.
is_symbol_char(X) :- print(X), nl, \+ member(X, [":"]).

:- is_symbol_char("x").
:- \+ is_symbol_char(":").
:- symbol_char(["x"], []).
:- \+ symbol_char([":"], []).

:- symbol(["aY:"],[]).
