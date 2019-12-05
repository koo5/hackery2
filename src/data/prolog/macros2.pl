:- module(_, [
		user:goal_expansion/2]).


:- multifile user:goal_expansion/2.
:- dynamic user:goal_expansion/2.


/*executed at compile time, passess X through, and binds Names to info suitable for term_string*/

user:goal_expansion(
	compile_with_variable_names_preserved(X, variable_names(Names))
, X) :-
	term_variables(X, Vars),
	maplist(my_variable_naming, Vars, Names).

/*compile_with_variable_names_preserved usage:
x([S2,' ', S3,' ', S4]) :-
	compile_with_variable_names_preserved((
		AC=4444*X,
		X = Z/3,
		true
	), Namings),
	compile_with_variable_names_preserved((
		AC=4444*X,
		X = Z/3,
		true
	), Namings),
	Z = 27,
	writeln(''),
	print_term(AC, [Namings]),
	writeln(''),
	compile_with_variable_names_preserved((
		AC2=4*XX,
		XX = Z/3,
		true
	), Namings2),
	writeln(''),
	print_term(AC2, [Namings2]),
	writeln(''),
	true.
:- x(S).
*/

/*
goal_expansion of magic_formula this takes X, which is the parsed terms, and returns Code, at compile time.
Code can actually be printed out, and we should probably split this into two phases,
where the first generates an actual source file.
At any case there are some tradeoffs to consider, and i think this is more of a fun hack that can get
some simple calculators into production quickly, not a perfect solution.
*/
user:goal_expansion(
	magic_formula(X), Code
) :-
	term_variables(X, Vars),
	maplist(my_variable_naming, Vars, Names),
	Namings = variable_names(Names),
	expand_formulas(Namings, X, [], Expansions),
	expand_formulas_to_code(Expansions, Code)/*,
	Code = (AAA,BBB,_),
	writeln(AAA),
	writeln('------')
	writeln(BBB),
	writeln('------')*/.

expand_formulas_to_code([], (true)).

expand_formulas_to_code([H|T], Expansion) :-
	H = (New_Formula, S1, Description, _A),
	New_Formula = (V is Rhs),
	Expansion = ((
		writeln(''),
		%write('<!-- '), write(S1), writeln(': -->'),
		write('<!-- '), writeln(' -->'),
		assertion(ground(((S1,Rhs)))),
		New_Formula,
		/*nonvar(V), silence singleton variable warning, doesn't work */
		utils:open_tag(S1),  format('~2f', [V]), utils:close_tag(S1),
		write_tag([S1, '_Formula'], Description),
		term_string(Rhs, A_String),
		atomic_list_concat([S1, ' = ', A_String], Computation_String),
		write_tag([S1, '_Computation'], Computation_String)
		), Tail),
	expand_formulas_to_code(T, Tail).

expand_formula(Namings, (A=B), _Es_In, ((A is B), S1, Description, A)):-
	term_string(A, S1, [Namings]),
	term_string(B, S2, [Namings]),
	atomic_list_concat([S1, ' = ', S2], Description).

expand_formulas(Namings, (F, Fs), Es_In, Es_Out) :-
	expand_formula(Namings, F, Es_In, E),
	append(Es_In, [E], Es2),
	expand_formulas(Namings, Fs, Es2, Es_Out),!.

expand_formulas(Namings, F,  Es_In, Es_Out) :-
	expand_formula(Namings, F, Es_In, E),
	append(Es_In, [E], Es_Out).

my_variable_naming(Var, (Name = Var)) :-
	var_property(Var, name(Name)).




/* take a list of variables, produce a dict with lowercased variable names as keys, and variables themselves as values.
see plunit/utils for examples*/
user:goal_expansion(
	dict_from_vars(Dict, Vars_List), Code
) :-
	maplist(var_to_kv_pair, Vars_List, Pairs),
	Code = dict_create(Dict, _, Pairs).

user:goal_expansion(
	dict_from_vars(Dict, Name, Vars_List), Code
) :-
	maplist(var_to_kv_pair, Vars_List, Pairs),
	Code = dict_create(Dict, Name, Pairs).

var_to_kv_pair(Var, Pair) :-
	var_property(Var, name(Name)),
	downcase_atom(Name, Name_Lcase),
	Pair = Name_Lcase-Var.
/*
user:goal_expansion(A,B) :-
    (nonvar(B) -> (writeq((A,B)),nl,nl) ; true),
    A = xxx(X),
    B = yyy(X),
    true.
*/
/*
user:goal_expansion(xxx(X),yyy(X)) :-
    true.
*/

user:goal_expansion(
	dict_vars(Dict, Tag, Vars_List), Code
) :-
	Code = (is_dict(Dict, Tag), Code0),
	dict_vars_assignment(Vars_List, Dict, Code0).

user:goal_expansion(
	dict_vars(Dict, Vars_List), Code
) :-
	(dict_vars_assignment(Vars_List, Dict, Code) -> true ; (format(user_error, 'xxxxx', []))).

dict_vars_assignment([Var|Vars], Dict, Code) :-
	Code = (Code0, Codes),
	Code0 = (debug(dict_vars, '~w', [Key]), get_dict(Key_Lcase, Dict, Var)),
    (
        (
            var_property(Var, name(Key)),
            downcase_atom(Key, Key_Lcase)
        )
    ->
        true
    ;
        (writeq(Code), nl, nl/*, Key_Lcase = yy*/)
    ),
    dict_vars_assignment(Vars, Dict, Codes).

dict_vars_assignment([], _, true).

x(D) :-
    gtrace,
    dict_vars(D, [YY, ZZ]),
    writeln(YY),
    writeln(YY),
    writeln(ZZ),
    writeln(ZZ).

aaa:-nl.

yyy.
yyy(Y) :- writeq(Y).


:- debug,/*trace,*/x(_{yy:88, zz:99}), halt.
