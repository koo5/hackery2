% https://en.wikipedia.org/wiki/Backus%E2%80%93Naur_form#Introduction


use_module(library(dcg/basics)). 


symbol --> string_without([":"], Rest).

:- symbol(["aY:"],[]).
