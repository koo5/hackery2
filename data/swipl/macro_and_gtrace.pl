:- use_module(library(fnotation)).
:- fnotation_ops($>,<$).
:- op(900,fx,<$).

:- op(812,fx,!).


user:goal_expansion(xxx(X), X).
user:goal_expansion(T, Y) :-
	nonvar(T), var(Y), T = yyy(Y).
x :-
	xxx(nl).
y :-
	writeq($>atom_string(abc)).
	
'!'(X,Y) :-
	Y = X.
'!'(_).

z(S_Transaction) :-
	
	debug(zz, 
		'processing source transaction:~n ~w~n', [
			$>!pretty_st_string(S_Transaction)]),
	(	current_prolog_flag(die_on_error, true)
	->	E = something_that_doesnt_unify_with_any_error
	;	true).

zz :-
	z(X),
	writeq(X),nl.

aa :-
	preprocess_s_transactions2(
		S_Transactions,
		Processed_S_Transactions,
		Transactions_Out,
		Outstanding_In,
		Outstanding_Out
	),
	writeq((
		S_Transactions,
		Processed_S_Transactions,
		Transactions_Out,
		Outstanding_In,
		Outstanding_Out
	)).
	
bb :-
	preprocess_s_transactions2_b(
		S_Transactions,
		Processed_S_Transactions,
		Transactions_Out,
		Outstanding_In,
		Outstanding_Out
	),
	writeq((
		S_Transactions,
		Processed_S_Transactions,
		Transactions_Out,
		Outstanding_In,
		Outstanding_Out
	)).
	

push_format(_,_).
pop_context.


preprocess_s_transaction3(_,_,_,_,_,_,_).
preprocess_s_transactions(_,_,_,_,_).

 preprocess_s_transactions2(
	[S_Transaction|S_Transactions],
	Processed_S_Transactions,
	Transactions_Out,
	Outstanding_In,
	Outstanding_Out
) :-
	!pretty_st_string(S_Transaction, Psss),
	push_format(
		'processing source transaction:~n ~w~n', [
			Psss]),

	(	current_prolog_flag(die_on_error, true)
	->	E = something_that_doesnt_unify_with_any_error
	;	true),

	catch_with_backtrace(
		!preprocess_s_transaction3(
			S_Transaction,
			Outstanding_In,
			Outstanding_Mid,
			Transactions_Out_Tail,
			Processed_S_Transactions,
			Processed_S_Transactions_Tail,
			Transactions_Out
		),
		E,
		(
		/* watch out: this re-establishes doc to the state it was before the exception */
			!handle_processing_exception(E)
		)
	),

	pop_context,

	(	var(E)
	->	(
			% recurse
			preprocess_s_transactions(
				S_Transactions,
				Processed_S_Transactions_Tail,
				Transactions_Out_Tail,
				Outstanding_Mid,
				Outstanding_Out
			)
		)
	;	(
			% give up
			Outstanding_In = Outstanding_Out,
			Transactions_Out = [],
			Processed_S_Transactions = []
		)
	).

 preprocess_s_transactions2_b(
	[S_Transaction|S_Transactions],
	Processed_S_Transactions,
	Transactions_Out,
	Outstanding_In,
	Outstanding_Out
) :-
	push_format(
		'processing source transaction:~n ~w~n', [
			$>!pretty_st_string(S_Transaction)]),

	(	current_prolog_flag(die_on_error, true)
	->	E = something_that_doesnt_unify_with_any_error
	;	true),

	catch_with_backtrace(
		!preprocess_s_transaction3(
			S_Transaction,
			Outstanding_In,
			Outstanding_Mid,
			Transactions_Out_Tail,
			Processed_S_Transactions,
			Processed_S_Transactions_Tail,
			Transactions_Out
		),
		E,
		(
		/* watch out: this re-establishes doc to the state it was before the exception */
			!handle_processing_exception(E)
		)
	),

	pop_context,

	(	var(E)
	->	(
			% recurse
			preprocess_s_transactions(
				S_Transactions,
				Processed_S_Transactions_Tail,
				Transactions_Out_Tail,
				Outstanding_Mid,
				Outstanding_Out
			)
		)
	;	(
			% give up
			Outstanding_In = Outstanding_Out,
			Transactions_Out = [],
			Processed_S_Transactions = []
		)
	).


		





/*



i can't reproduce the issue with the above code, but turns out you can `debug(gtrace(source)),debug(gtrace(position))`,
and then, gtracing my actual problematic code produces:


% [Thread pce] source for #23748200: 
% [Thread pce] Show source, PC = 86, Port = call
% [Thread pce] ClauseRef = <clause>(0x557290686ea0), PC = 86
% [Thread pce] Term-position: for ref=<clause>(0x557290686ea0) at PC=86: [2,2,2,2,2,2,2,1]
% [Thread pce] show_source(23748200,[gui(@17566584388282/prolog_debugger),pc(86),source,bindings,style(frame)]) failed







*/