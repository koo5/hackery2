:- use_module(library(chr)).

:- chr_constraint  design_check/0, wire/2, pin_not_checked/1.

design_check, wire(T, U) ==> pin_not_checked(T), pin_not_checked(U).
design_check, pin_not_checked(T) \ pin_not_checked(T) <=> true. % get rid of duplicates
design_check, wire(T, A), wire(T, B) \ pin_not_checked(T) <=> A \= B | true.
design_check, pin_not_checked(T) <=> format('singleton pin ~q', [T]).



