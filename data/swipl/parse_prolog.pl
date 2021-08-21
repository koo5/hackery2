:- write('continued in: https://github.com/lodgeit-labs/FOL_solvers/tree/tracer1/prolog/parse_prolog'),halt.

/*
	this is a proof-of-concept of obtaining prolog AST, inspired by https://github.com/SWI-Prolog/packages-indent/blob/master/indent.pl
	maybe this is doing it better: ?
		https://www.swi-prolog.org/pldoc/doc/_SWI_/library/prolog_colour.pl?show=src#prolog_colourise_stream/3
*/

:- use_module(library(prolog_source)).
:- use_module(library(pprint)).
:- use_module(library(listing)).
:- use_module(library(apply)).
:- use_module(library(http/json)).

:- dynamic opened_file/1.
:- dynamic opened_file/2.

cmdline_main :-
	ArgSpec = [
		[opt(fn), type(atom), shortflags([f]), longflags([fn]),
			help('the main .pl file of your codebase')]],
	current_prolog_flag(argv, Args),
	opt_parse(ArgSpec , Args, Opts, []),
	memberchk(fn(Fn), Opts),
	run(Fn).

run(Source_File_Specifier) :-
	open_and_parse_file(Source_File_Specifier,_).

open_and_parse_file(Source_File_Specifier,Fn) :-
	(	exists_source(Source_File_Specifier, Fn)
	->	open_and_parse_file2(Fn)
	;	Fn = error("doesn't look like something i can load:")).
	
open_and_parse_file2(Fn) :-	
	(	opened_file(Fn)
	->	true
	;	(
			setup_call_cleanup(
				open(Fn, read, In),
				(
					assert(opened_file(Fn)),
					debug(parse_prolog(files), 'now reading ~q', [Fn]),
					read_src(In,Ast),
					assert(opened_file(Fn,Ast)),
					%maplist(write_ast_line,Ast),
					true
				),
				close(In)
			)
		)
	).

read_src(In,[Clause|Tail]) :-
	prolog_read_source_term(In, Term, Expanded,
				[ variable_names(Vars),
				  term_position(Start),
				  subterm_positions(Layout),
				  comments(Comment),
				  operators(Ops)
				]),
	Clause0 = clause{
              term:(Term),
			  expanded:(Expanded),
		      variables:(Vars),
		      input:(In),
		      start:(Start),
		      layout:(Layout),
		      comment:(Comment)
	},
	write_ast_line(Clause0),
	dif(Expanded, end_of_file),
	recurse(Expanded, Imports),
	Clause = Clause0.put(imports, Imports),
	!,
	read_src(In,Tail).
	
read_src(_,[end]) :- true.

recurse(X, Imports) :-
	(
		(
			X = ':-'(Specifiers),
			is_list(Specifiers)
		)
	;	(
			X = ':-'(use_module(Specifiers)),
			is_list(Specifiers)
		)
	;	(
			X = ':-'(use_module(Specifier)),
			\+is_list(Specifier),
			Specifiers = [Specifier]
		)
	;	(
			/* we dont care about explicit import lists. Resolving predicate names or somesuch is out of scope of this script. */
			X = ':-'(use_module(Specifier,_Imports)),
			Specifiers = [Specifier]
		)
	),
	!,
	maplist(make_import,Specifiers,Imports).
	
recurse(_, []) :- true.	

make_import(Specifier,import(Specifier,Fn)) :-
	open_and_parse_file(Specifier,Fn).


write_ast_line(Ast) :-
	json_write(user_output, Ast, [serialize_unknown(true)]),
	nl.


/*
it works like this right now:

swipl -s parse_prolog.pl -g "debug,run('parseme.pl'),halt."
:-use_module(ops)

:-module(_40382,[op(812,fx,!),op(812,fx,?)])

:-dynamic ddd/0

x:-y

end_of_file

:-['dep.pl']

:-assert(ddd)

x:-ddd(!lalala,!tralala)

:-['parseme.pl']

end_of_file

!blabla

:-ddd

end_of_file

koom@dev ~/work/hackery2/data/swipl (master)> 






*/






/*

for now unused stuff from indent.pl :

%%	term_pi(+Term, -PI)

term_pi(Head :- _, PI) :- !,
	head_pi(Head, PI).
term_pi(Head --> _, PI) :- !,
	dcg_head_pi(Head, PI).
term_pi(Head, PI) :-
	head_pi(Head, PI).

head_pi(M:Head, M:PI) :- !,
	plain_head_pi(Head, PI).
head_pi(Head, PI) :-
	plain_head_pi(Head, PI).

dcg_head_pi(M:Head, M:PI) :-
	dcg_plain_head_pi(Head, PI).
dcg_head_pi(Head, PI) :-
	dcg_plain_head_pi(Head, PI).

plain_head_pi(Head, Name/Arity) :-
	functor(Head, Name, Arity).
dcg_plain_head_pi(Head, Name//Arity) :-
	functor(Head, Name, Arity).

canonical_pi(M:PI0, M:PI) :- !,
	canonical_pi(PI0, PI).
canonical_pi(Name//Arity0, Name/Arity) :- !,
	Arity is Arity0 + 2.
canonical_pi(PI, PI).

%%	indent_to_column(+Out, +Indent)
%
%	Indent to column Indent. Uses   the setting listing:tab_distance
%	to determine the mapping between tabs and spaces.

indent_to_column(Out, N) :-
	nl(Out),
	setting(listing:tab_distance, D),
	(   D =:= 0
	->  tab(Out, N)
	;   Tab is N // D,
	    Space is N mod D,
	    put_tabs(Out, Tab),
	    tab(Out, Space)
	).

put_tabs(Out, N) :-
	N > 0, !,
	put(Out, 0'\t),
	NN is N - 1,
	put_tabs(Out, NN).
put_tabs(_, _).

*/







/*
indent(Clause, _, _) :-
	clause_term(Clause, end_of_file), !.
indent(Clause, In, Out) :-
	read_predicate(Clause, Clauses, Next, In),
	indent_predicate(Out, Clauses),
	indent(Next, In, Out).
*/



%%	read_predicate(+Clause0, -Clauses, -NextClause, +In) is det.
%
%	Read the next predicate from the source
/*
read_predicate(Clause0, [Clause0|Rest], Next, In) :-
	read_src(In, Clause1),
	(   same_pred(Clause0, Clause1)
	->  read_predicate(Clause1, Rest, Next, In)
	;   Next = Clause1,
	    Rest = []
	).

same_pred(Clause1, Clause2) :-
	clause_pred(Clause1, PI1),
	clause_pred(Clause2, PI2),
	canonical_pi(PI1, PI),
	canonical_pi(PI2, PI).

clause_pred(Clause, PI) :-
	clause_term(Clause, Term),
	term_pi(Term, PI).







%%	indent_predicate(+Out, +Clauses) is det.
%
%	Indent a single predicate.

indent_predicate(Out, Clauses) :-
	maplist(indent_clause(Out), Clauses),
	format(Out, '~n', []).

indent_clause(Out, Clause0) :-
	leading_comments(Clause0, Clause1, Out),
	annotate_clause(Clause1, Clause),
	clause_variables(Clause, Vars),
	bind_vars(Vars),
	clause_term(Clause, Term),
	print_term(Term,[
			tab_width(1),
			indent_arguments(1),
			right_margin(200)
			
		]),
	nl,nl,
	writeq(Clause),
	%gtrace,
	nl,nl,
	portray_clause(Out, Term, [portray_goal(indent_portray)]).

leading_comments(ClauseIn, ClauseOut, Out) :-
	clause_layout(ClauseIn, Layout),
	arg(1, Layout, StartClause),
	clause_comment(ClauseIn, Comment),
	leading_comments(Comment, StartClause, RestComments, Out),
	set_comment_of_clause(RestComments, ClauseIn, ClauseOut).


%%	leading_comments(+Comments, +StartClause, -InClauseComment, +Out)
%
%	Emit the comments that preceed the clause.
%
%	@param	StartClause is the character offset that starts the
%		clause
%	@tbd	(optionally) reformat the comments

leading_comments([], _, [], _) :- !.
leading_comments([Pos-Comment|Rest], StartClause, RestComments, Out) :-
	stream_position_data(char_count, Pos, StartComment),
	StartComment < StartClause, !,
	stream_position_data(line_position, Pos, LinePos),
	indent_to_column(Out, LinePos),
	format(Out, '~s~n~n', [Comment]),
	leading_comments(Rest, StartClause, RestComments, Out).
leading_comments(Comments, _, Comments, _).


bind_vars([]).
bind_vars([Name=Var|T]) :-
	Var = '$VAR'(Name),
	bind_vars(T).

%%	annotate_clause(+ClauseIn, +In, -ClauseOut) is det.
%
%	Annotate ClauseIn with additional information such as particular
%	encodings of numbers or  the  use   of  strings.  This also adds
%	comments as annotations to the clause structure.

annotate_clause(ClauseIn, ClauseOut) :-
	clause_term(ClauseIn, Term),
	clause_layout(ClauseIn, Layout),
	clause_comment(ClauseIn, Comments),
	clause_source(ClauseIn, Source),
	annotate(Term, Layout, Comments, Source, TermOut),
	set_term_of_clause(TermOut, ClauseIn, ClauseOut).

annotate(String, Pos, _, Source, '$listing'(String, string(Text))) :-
	Pos = string_position(_,_), !,
	source_text(Source, Pos, Text).
annotate(Number, Pos, _, Source, '$listing'(Number, number(Text))) :-
	number(Number), !,
	source_text(Source, Pos, Text).
annotate(Primitive, _-_, _, _, Primitive) :- !.
annotate({}(Arg), brace_term_position(F,T,ArgPos), Comments, Source, TermOut) :-
	!,
	include(comment_in_range(F-T), Comments, EmbeddedComments),
	annotate(Arg, ArgPos, EmbeddedComments, Source, TermOut).
annotate(List, list_position(F,T,Elms,Tail), Comments, Source, ListOut) :- !,
	include(comment_in_range(F-T), Comments, EmbeddedComments),
	annotate_list(List, Elms, Tail, EmbeddedComments, Source, ListOut).
annotate(Term, term_position(F,T,_,_,ArgPos), Comments, Source, TermOut) :-
	functor(Term, Name, Arity),
	functor(TermOut, Name, Arity),
	include(comment_in_range(F-T), Comments, EmbeddedComments),
	annotate_args(1, Term, ArgPos, EmbeddedComments, Source, TermOut).

annotate_list([H|T], [PH|PT], TP, Comments, Source, [AH|AT]) :- !,
	annotate(H, PH, Comments, Source, AH),
	annotate_list(T, PT, TP, Comments, Source, AT).
annotate_list([], [], none, _, _, []) :- !.
annotate_list(Last, _, TP, Comments, Source, ALast) :-
	annotate(Last, TP, Comments, Source, ALast).

annotate_args(_, _, [], _, _, _) :- !.
annotate_args(I, Term, [PH|PT], Comments, Source, TermOut) :-
	arg(I, Term, A0),
	arg(I, TermOut, A),
	partition(comment_in_range(PH), Comments, A0Comments, RComments),
	annotate(A0, PH, A0Comments, Source, A1),
	(   PT = [PR|_]
	->  split_comments(RComments, PR, Now, RestComments)
	;   Now = RComments,
	    RestComments = []
	),
	tag_comment(Now, A1, A),
	succ(I, I2),
	annotate_args(I2, Term, PT, RestComments, Source, TermOut).

tag_comment([], Term, Term) :- !.
tag_comment(Comments, Term, '$comment'(Term, Comments)).

comment_in_range(Range, Pos-_) :-
	arg(1, Range, From),
	arg(2, Range, To),
	stream_position_data(char_count, Pos, Start),
	between(From, To, Start).

%%	split_comments(+Comments, +Pos, -Before, -After)
%
%	Split the set of Comments in a subset Before Pos and After Pos.

split_comments([], _, [], []).
split_comments([C0|CT], P, Before, After) :-
	C0 = Pos-_,
	stream_position_data(char_count, Pos, StartComment),
	arg(1, P, Here),
	(   StartComment < Here
	->  Before = [C0|BT],
	    split_comments(CT, P, BT, After)
	;   After = [C0|CT],
	    Before = []
	).


%%	source_text(+Source, +Pos, -Text:atom) is det.
%
%	Get the original source text for the range Pos.

source_text(Offset-Source, Pos, Text) :-
	arg(1, Pos, Start),
	arg(2, Pos, End),
	S is Start - Offset,
	L is End - Offset - S,
	sub_atom(Source, S, L, _, Text).

%%	clause_source(+Clause, -Source) is det.
%
%	Read the source-text for Clause from the original input
%
%	@param	Source is a term Offset-Text, where Offset is the
%		character position of the start and Text is an atom
%		representing the clause-text.

clause_source(ClauseIn, Start-Text) :-
	clause_input(ClauseIn, In),
	setup_call_cleanup(stream_property(In, position(Here)),
			   read_clause_text(ClauseIn, In, Start, Text),
			   set_stream_position(In, Here)).

read_clause_text(ClauseIn, In, StartCode, Text) :-
	clause_start(ClauseIn, Start),
	stream_position_data(char_count, Start, StartCode),
	clause_layout(ClauseIn, Layout),
	assertion(arg(1, Layout, StartCode)),
	arg(2, Layout, End),
	Count is End-StartCode,
	set_stream_position(In, Start),
	read_n_codes(Count, In, Codes),
	atom_codes(Text, Codes).

read_n_codes(N, In, [H|T]) :-
	succ(N2, N), !,
	get_code(In, H),
	read_n_codes(N2, In, T).
read_n_codes(_, _, []).

%%	indent_portray(+Term)
%
%	Use a local portray hook that   allows us to format annotations.
%	Note that for numbers,  strings,  etc.   we  can  choose between
%	emitting  the  original  token   or    generating   a   caonical
%	representation for the value.
%
%	@see '$put_quoted'/4 supports emitting escaped quoted strings.

:- public
	indent_portray/2.

indent_portray('$listing'(_String, string(Text)), _Options) :-
	write(Text).
indent_portray('$listing'(_Number, number(Text)), _Options) :-
	write(Text).
indent_portray('$comment'(Term, Comments), Options) :-
	memberchk(priority(Pri), Options),
	prolog_listing:pprint(current_output, Term, Pri, Options),
	print_comments(Comments).

print_comments([]).
print_comments([_Pos-Comment|T]) :-
	write(Comment),
	print_comments(T).




*/


