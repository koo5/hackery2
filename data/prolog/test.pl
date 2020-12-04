%a(A) :-
%	term_string(A, S, [variable_names(VNames)]), writeln(S), writeln(VNames).






b(L) :-
	term_to_atom(L, Eqs, A), writeln(Eqs), writeln(A).


term_to_atom(T, Eqs, A) :-
   with_output_to(atom(A), write_term(T,[variable_names(Eqs),quoted(true)]) ).


:- C = 1, b([C]).