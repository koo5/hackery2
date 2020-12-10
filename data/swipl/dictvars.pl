:- debug.

%:- ['../../../../lodgeit2/master2/sources/public_lib/lodgeit_solvers/prolog/utils/dict_vars.pl'].

/*user:goal_expansion(
	dict_from_vars(Dict, Vars_List), L0, Code, L0
) :-
	writeq(L0),nl,
	maplist(var_to_kv_pair, Vars_List, Pairs),
	Code = dict_create(Dict, _, Pairs).
*/
user:goal_expansion(
	dict_from_vars(Dict, Vars_List), L, Code, L
) :-
	maplist(var_to_kv_pair, Vars_List, Pairs),
	Code = (dict_create, writeq(dict_from_vars(Dict, Vars_List)))/*(Dict, _, Pairs)*/.


var_to_kv_pair(Var, Pair) :-
	var_property(Var, name(Name)),
	downcase_atom(Name, Name_Lcase),
	Pair = Name_Lcase-Var.



a :-
	dict_from_vars(Dict, [V,VV,VVV]),
	V = 0,
	VV is 1/3,
	VVV = 3,
	writeq((Dict, V, VV, VVV)),nl.
	


