#!/usr/bin/env swipl

:- use_module(library(dcg/basics)).

process :-
    (   read_line_to_codes(user_input, Line)
    ->  (
            (   phrase(is_a_socket((Fn1,Fn2)), Line)
            ->  (
                    writeq(['rm ', Fn1]),
                    writeq(['rm ', Fn2])
                )
            ;   true),
            process
        )
    ;   true).

is_a_socket((Fn1,Fn2)) --> 'File ', string(Fn1), ' is a socket while file ', string(Fn2), ' is a socket'.

:- process,halt.
