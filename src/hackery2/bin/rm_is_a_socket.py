#!/usr/bin/env swipl

:- use_module(library(dcg/basics)).




shell2(Cmd) :-
        shell2(Cmd, _).

shell2(Cmd_In, Exit_Status) :-
        flatten([Cmd_In], Cmd_Flat),
        atomic_list_concat(Cmd_Flat, Cmd),
        format(user_error, '~w\n\n', [Cmd]),
        shell(Cmd, Exit_Status).




process :-
    (   read_line_to_codes(user_input, Line)
    ->  (
            (   phrase(is_a_socket((Fn1,Fn2)), Line)
            ->  (
                    string_codes(N1, Fn1),
                    string_codes(N2, Fn2),
                    shell2(['rm ', N1]),nl,
                    shell2(['rm ', N2]),nl
                )
            ;   true),
            process
        )
    ;   true).

is_a_socket((Fn1,Fn2)) --> `File `, string(Fn1), ` is a socket while file `, string(Fn2), ` is a socket`.

is_a_socket((Fn1,Fn2)) --> `File `, string(Fn1), ` is a fifo while file `, string(Fn2), ` is a fifo`.



:- process,halt.


% cat dif12 | grep -v socket | grep -v fifo
