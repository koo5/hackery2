/*
	this is a proof-of-concept of obtaining prolog AST, inspired by https://github.com/SWI-Prolog/packages-indent/blob/master/indent.pl
	
	alternatives:
		https://github.com/lodgeit-labs/FOL_solvers/blob/tracer1/wiki/SWIPL-and-prolog-notes.md#parsing-prolog-code
		
	limitations:
		there isnt any logic to implement conditional compilation (`:- if ...`), so this won't handle conditionally declared ops .
		
	nomenclature:
		import:
			use_module(....
		include:
			:- [file1,...

	wontfix?:
		cyclic includes:
			swipl itself chokes on cyclic includes
		
	todo:
		representation of parsed code:
		
		

*/

:- use_module(library(prolog_source)).
:- use_module(library(pprint)).
:- use_module(library(listing)).
:- use_module(library(apply)).
:- use_module(library(http/json)).
:- use_module(library(prolog_source), [expand/4]).

:- dynamic seen/1.
:- dynamic seeing/1.

cmdline_main :-
	ArgSpec = [
		[opt(fn), type(atom), shortflags([f]), longflags([fn]),
			help('file path string -- the main .pl file of your codebase')],
		[opt(sp), type(atom), shortflags([s]), longflags([spec]),
			help('prolog term / file specifier -- the main .pl file of your codebase')]
	],
	current_prolog_flag(argv, Args),
	opt_parse(ArgSpec , Args, Opts, []),
	(	memberchk(fn(Fn0), Opts)
	->	run(Fn0)
	;	(	memberchk(sp(Fn0), Opts)
		->	(
				term_string(Fn, Fn0),
				run(Fn)
			)
		)
	).

run(Source_File_Specifier) :-
	do_import([], Source_File_Specifier, _, _).


do_import(Ctx_Given, Source_File_Specifier, import{specifier: Source_File_Specifier, fn: Fn}, Ctx_Exported) :-
	T = seen(Source_File_Specifier, Fn, Ctx_Exported),
	(	seen(T)
	->	debug(parse_prolog(seen), 'seen. skipping: ~q', [T])
	;	(	exists_source(Source_File_Specifier, Fn)
		->	(
				/*(	seeing(Fn)
				->	throw(err('we be cyclin\'', Source_File_Specifier))
				;	true)*/
				%assert(seeing(Fn)),
				setup_call_cleanup(
					open(Fn, read, In),
					(
						debug(parse_prolog(files), 'now reading ~q', [Fn]),
						read_src(Source_File_Specifier,Fn,In,_,Ctx_Given,[],Ctx_Exported),
						assert(seen(T))					
					),
					close(In)
				),
				retractall(seeing(Fn))
			)
		;	(
				/* https://github.com/SWI-Prolog/swipl-devel/issues/715 ?
				or this looks more like i fail to give exists_source a path to start from? */
				(	member(Source_File_Specifier, [clpq/bv_q,clpq/fourmotz_q,clpq/ineq_q,clpq/itf_q,clpq/nf_q,clpq/store_q,clpqr/class,clpqr/dump,clpqr/geler,clpqr/itf,clpqr/ordering,clpqr/project,clpqr/redund])
				->	(
						Ctx_Exported = [],
						debug(parse_prolog(files), 'ignoring unimportable specifier: ~q', [Source_File_Specifier])
					)
				;	throw(err('doesnt look like something i can load', Source_File_Specifier))
				)
			)
		)
	).



/*
recurse on a list of clauses read from a file. 
*/

read_src(/*+*/Source_File_Specifier,/*+*/Fn,/*+*/In, /*-*/[Clause|Clauses], /*+*/Ctx_at_import_site, /*+*/Ctx_Local, /*-*/Ctx_Exported) :-
	append(Ctx_at_import_site, Ctx_Local, Ctx_Current),
	ctx_ops(Ctx_Current, Ops),
	debug(parse_prolog(ops), 'read with ops: ~q', [Ops]),
	push_operators(Ops),

/*
	prolog_read_source_term(In, Term, Expanded,
				[ 
				  syntax_errors(error),
				  variable_names(Vars),
				  term_position(Start),
				  subterm_positions(Layout),
				  comments(Comment)
				  %,operators(Ops)
				]),
*/

	read_clause(In, Term,
				[ 
				  syntax_errors(error),
				  variable_names(Vars),
				  term_position(Start),
				  subterm_positions(Layout),
				  comments(Comment)
				]),

	expand(Term, Layout, In, Expanded),

	pop_operators,

	Clause0 = clause{
              term:(Term),
			  expanded:(Expanded),
		      variables:(Vars),
		      %input:(In),
		      start:(Start),
		      layout:(Layout),
		      comment:(Comment)
	},
	write_ast_line(Clause0),

	(	Expanded = end_of_file
	->	(
			Clause = end,
			Ctx_Local = Ctx_Exported
		)
	;	
		(

			(	Expanded = ':-'(module(_, _, _Dialect))
			->	throw(not_supported_yet(Expanded))
			;	true),

			(	Expanded = ':-'(module(_))
			->	throw(not_supported_yet(Expanded))
			;	true),

			/* 
			when the file is a module, only the explicitly exported ops are passed back to the including location
			when it is a plain file, all ops declared within are passed back
			*/
			
			(	Expanded = ':-'(module(_, PublicList))
			->	(

					exportlist_ops(PublicList, Ops_exported_from_here),
					Ctx_Exported = Ops_exported_from_here,
					
					/* cut off right after module declaration, if this is a library, as opposed to user code? */
					(	false%Source_File_Specifier = library(_)
					->	Clauses = []
					;	(
							(	seeing(Fn)
							->	(
									debug(parse_prolog(files), 'cycle detected, not reading body of module ~q now.', [Fn]),
									Clauses = []
								)
							;	(
									assert(seeing(Fn)),
									append(Ctx_Local, Ops_exported_from_here, Ctx_Local2),
									read_src(Source_File_Specifier,Fn,In,Clauses,Ctx_at_import_site,Ctx_Local2,_)
								)
							)
						)
					)
						
							
				)
			;	(
					/* this line isnt a module declaration, just an ordinary statement or an import */
					(	maybe_do_imports(Ctx_Current, Expanded, Imports, Imported_ops)
					->	(	
							Clause = Clause0.put(imports, Imports),
							append(Ctx_Local, Imported_ops, Ctx_Local2)
						)
					;	(
							(	(
									Expanded = ':-'(Op),
									Op = op(_,_,_)
								)
							->	append(Ctx_Local, [Op], Ctx_Local2)
							;	(
									Clause = Clause0,
									Ctx_Local2 = Ctx_Local
								)
							)
						)
					),
					debug(parse_prolog(ops), 'read next statement with local ops: ~q', [Ctx_Local2]),
					read_src(Source_File_Specifier,Fn,In,Clauses,Ctx_at_import_site,Ctx_Local2,Ctx_Exported)
				)
			)
		)
	).


/*
imports(Import)
    Specify what to import from the loaded module. The default for use_module/1 is all. Import is passed from the second argument of use_module/2. Traditionally it is a list of predicate indicators to import. As part of the SWI-Prolog/YAP integration, we also support Pred as Name to import a predicate under another name. Finally, Import can be the term except(Exceptions), where Exceptions is a list of predicate indicators that specify predicates that are not imported or Pred as Name terms to denote renamed predicates. See also reexport/2 and use_module/2.bug

    If Import equals all, all operators are imported as well. Otherwise, operators are not imported. Operators can be imported selectively by adding terms op(Pri,Assoc,Name) to the Import list. If such a term is encountered, all exported operators that unify with this term are imported. Typically, this construct will be used with all arguments unbound to import all operators or with only Name bound to import a particular operator.
*/
	
	
maybe_do_imports(Ctx_Given, X, Ast, Ctx_exported_final) :-
	(
		(
			X = ':-'(use_module(Files)),
			is_list(Files),
			findall(use_module(F, all), member(F,Files), Imports)
		)
	;	(
			X = ':-'(Files),
			is_list(Files),
			/*
			the action of including a module seems to have the same semantics as importing it. Ops declared as exported from the module are seen in the including file, while ops declared in the body are not.
			*/
			findall(use_module(F, all), member(F,Files), Imports)
		)
	;	(
			X = ':-'(use_module(File)),
			\+is_list(File),
			Imports = [use_module(File, all)]
		)
	;	(
			X = ':-'(use_module(File, ImportList)),
			Imports = [use_module(File, ImportList)]
		)
	),
	do_imports(Ctx_Given, Imports, Ast, [], Ctx_exported_final),
	debug(parse_prolog(ops), 'imported ops: ~q', [Ctx_exported_final]).

do_imports(_, [], [], Ctx_exported_final, Ctx_exported_final).

do_imports(Ctx_Given,
		   [use_module(File, ImportList)|Specifiers],
		   [Ast|Asts],
		   Ctx_Exported,
		   Ctx_exported_final)
:-
	debug(parse_prolog(imports), 'import: ~q', [File]),
	'append exported ops to context'(Ctx_Given, Ctx_Exported, Ctx_Local),
	do_import(Ctx_Local, File, Ast, ExportedOps),
	op_matchers(ImportList, Matchers),
	matching_exported_ops(Matchers, ExportedOps, ImportedOps),
	debug(parse_prolog(ops), 'importing ops: ~q', [ImportedOps]),
	'append exported ops to context'(Ctx_Exported, ImportedOps, Ctx_Middle),
	do_imports(Ctx_Given, Specifiers, Asts, Ctx_Middle, Ctx_exported_final).


'append exported ops to context'(Ctx_Accum, Export_List, Ctx_Middle) :-
	exportlist_ops(Export_List, ImportedOps),
	append(Ctx_Accum, ImportedOps, Ctx_Middle).


exportlist_ops(Export_List, Ops) :-
	findall(
		Op,
		(
			member(Op, Export_List),
			(
				Op = op(_,_,_)
			;
				Op = op(_,_)
			)
		),
		Ops0
	),
	sort(Ops0, Ops).


write_ast_line(Ast) :-
	(	debugging(parse_prolog(ast))
	->	json_write(user_output, Ast, [serialize_unknown(true)]),nl
	;	true).

ctx_ops(Ctx,Ops) :-
	exportlist_ops(Ctx,Ops).

op_matchers(except(ExceptList), ImportedOpMatchers) :-
	!,
	maplist(dif(X), ExceptList),
	ImportedOpMatchers = [X].

op_matchers(ImportList, ImportedOpMatchers) :-
	(	ImportList = all
	->	ImportedOpMatchers = [_]
	;	exportlist_ops(ImportList, ImportedOpMatchers)).

matching_exported_ops(Matchers, ExportedOps, ImportedOps) :-
	findall(
		Matcher,
		(
			member(Matcher, Matchers),
			member(Matcher, ExportedOps)
		),
		ImportedOps0
	),
	sort(ImportedOps0,ImportedOps).


/*


========


*/

%find_term(..














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


