%!  path_term_to_list__fl(+Term_In, -List_Out) is det.
%
%   Takes a term in the form aaa/bbb/ccc/..., that is, through default
%   operator priority, ((aaa/bbb)/ccc)/..., and produces a list:
%   [aaa, bbb, ccc...]
%

path_term_to_list__fl(Term_In, List_Out) :-
	imp((
		>Term = Term_In,
		while((<Done \= true),
		(
			(	Blob/Atom = <Term
			->	(	(atomic(Atom)->true;throw(zzz)),
					append([Atom], <List, >List),
					>Term = Blob,
				)	;	(
					append([Term], <List, >List),
					>Done = true
				)
			))
		),
		List_Out = <List 
	)).










runtime interpreter:
run(while(Cond, Loop)) :-
	call(Cond
	once(Loop)







compile time expansion:
	find all gSomething atoms,





imp((

	repeat,
	(
		gget(G, term, Term),
		(	glop(G,  Blob/Atom = Term
		->	(	
				(atomic(Atom)->true;throw(zzz)),
				g(G, append([Atom], gg(list), sg(list))),
				gset(G, term, Blob),
				gget(G, done, true)
			)
		;	g(G, append([Term], gg(list), sg(list))),
		),
		New_list)
	),
    nb_current(GDone, true).

)).



path_term_to_list__fl(Term_In, List_Out) :-
    gensym(state_of_imperative_procedure__path_term_to_list__fl__term,T),
    gensym(state_of_imperative_procedure__path_term_to_list__fl__list,L),
    b_setval(T, Term_In),
    b_setval(L, []),
    once(path_term_to_list__fl2((L,T))),
    b_getval(L, List_Out).
    
path_term_to_list__fl2((L,T)) :-
	repeat,
	(
		gget(G, term, Term),
		(	glop(G,  Blob/Atom = Term
		->	(	
				(atomic(Atom)->true;throw(zzz)),
				g(G, append([Atom], gg(list), sg(list))),
				gset(G, term, Blob),
				gget(G, done, true)
			)
		;	g(G, append([Term], gg(list), sg(list))),
		),
		New_list)
	),
    nb_current(GDone, true).



nb_setarg?


/*i guess we might as well do term rewriting, because we won't see our variables anyway.
might want to have a second window running where you paste the G, and it queries your process repeatedly and prints your vars.*/


/*glop(append([Atom], gg(GList), sg(GList))),*/
					nb_getval(GList, List),
					append([Atom], List, New_List),
					nb_setval(GList, New_List),


				gset(G, term, Blob),
===
				glop(G, sg(term) = Blob



sg(GKey, Functoor
$>nb_getval(GList))),


g(GKey, Old, New) :-
	nb_setval(GKey, New).
*/
