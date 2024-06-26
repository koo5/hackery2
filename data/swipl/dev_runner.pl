#!/usr/bin/env swipl

:- multifile user:message_hook/3.
user:message_hook(initialization_error(_,X,_),Kind,_) :- print_message(Kind,X),halt(1).
user:message_hook(string(S),_,_) :- format(user_error,'ERROR: ~w~n', [S]).

/*
running this takes a while because it first does just a load to find compile errors, and then runs swipl again to actually execute goal. Maybe next version will consult Script directly, but idk how to eval() a goal, except by parsing it first..
*/

shell2(Cmd) :-
	shell2(Cmd, _).

shell2(Cmd_In, Exit_Status) :-
	flatten([Cmd_In], Cmd_Flat),
	atomic_list_concat(Cmd_Flat, Cmd),
	%format(user_error, '~w\n\n', [Cmd]),
	shell(Cmd, Exit_Status).

maybe_halt_on_err :- 
	opts(Opts),
	memberchk(halt_on_problems(Halt), Opts),
	(	Halt = true
	->	halt_on_problems
	;	true).

halt_on_problems :-
	opts(Opts),
	(	(memberchk(problem_lines_whitelist(Whitelist_File), Opts), nonvar(Whitelist_File))
	->	Err_Grep = ['grep -E -i "Warn|err" err | grep -q -v -x -F -f ', Whitelist_File]
	;	Err_Grep = 'grep -q -E -i "Warn|err" err'
	),
	(	shell2(Err_Grep, 0)
	 ->	(
			format(user_error, "that's an error, halting.\n", []),
	 		halt(1)
		)
	;	true).

maybe_clean_terminal :-
	opts(Opts),
	memberchk(clear_terminal(Clear), Opts),
	(
		Clear = true
	->
		(
			shell2('timeout 0.1 reset'),
			shell2('echo "\e[3J" 1>&2'),
			shell2('timeout 0.1 reset')
		)
	;
		true
	).

x :- 
	Spec = [
		[opt(viewer), type(atom), shortflags([v]), longflags([viewer])]
		,[opt(debug), type(boolean), default(true), shortflags([d]), longflags([debug])]
		,[opt(halt_on_problems), type(boolean), default(true), shortflags([h]), longflags([halt_on_problems])]
		,[opt(problem_lines_whitelist), type(atom), longflags([problem_lines_whitelist])]
		,[opt(clear_terminal), type(boolean), default(false), shortflags([c]), longflags([clear_terminal])]
		,[opt(script), type(atom), shortflags([s]), longflags([script])]
		,[opt(goal), type(atom), shortflags([g]), longflags([goal])]
	],
	opt_arguments(Spec, Opts, Args),
	(Args = [] -> true ; throw(string('no positional arguments accepted'))),
	assert(opts(Opts)),
	format(user_error, '============...\n', []),
	opts(Opts),
	memberchk(debug(Debug), Opts),
	memberchk(viewer(Viewer), Opts),
	memberchk(script(Script), Opts),
	(nonvar(Script)->true;throw(string('-s needed'))),
	(	Debug = true
	->	Optimization = ''
	;	Optimization = '-O'),
	atomic_list_concat(['swipl ', Optimization, ' -s ', Script], Load_Cmd),
	maybe_clean_terminal,
	shell2([Load_Cmd, ' -g "make,halt."  2>&1  |  tee err | head -n 150']),
	maybe_halt_on_err,
	memberchk(goal(Goal), Opts),
	(	nonvar(Goal)
	->	(
			format(user_error, 'ok...\n', []),
			(	nonvar(Viewer)
			->	Redirection = ' 1> arrr.xml | tee err'
			;	Redirection = ''),
			shell2([Load_Cmd, ' -g "', Goal, ', halt."  2>&1 ', Redirection]),
			(	nonvar(Viewer)
			->	(maybe_halt_on_err, shell2([Viewer, ' arrr.xml']))
			;	true),
			halt
		)
	;	shell2([Load_Cmd],Exit),halt(Exit)).

:- initialization(x).
