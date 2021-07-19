p(p(4,6)).
p(p(1,5)).
p(p(2,4)).
p(p(2,3)).
p(p(2,6)).
p(p(3,5)).
p(p(3,4)).
p(p(1,2)).
p(p(6,6)).


path(p(B,C)) :- p(p(B,C)).
path(p(B,C)) :- p(p(C,B)).


start(p(3,1)).
start(p(1,3)).


path(Used,[Q|Rest],B,D) :-
	path(P), P = p(B,C),
	is_not_used(P, Used),
	P = Q,
	path(Used,Rest,C,D).	
	
path(Used,[Q],B,D) :-
	path(P), P = p(B,D),
	is_not_used(P, Used),
	P = Q.	

is_not_used(X,Useds) :-
	maplist(item_is_not_used(X), Useds).

item_is_not_used(_, Used_Item) :-		 
	var(Used_Item).
item_is_not_used(X, Used_Item) :-		 
	ground(Used_Item),
	X \= Used_Item,
	X = p(A,B),
	Used_Item \= p(B,A).


finish(Used) :-
	start(p(_,B)),
	length(Used,9),
	path(Used,Used,B,_C).


allsols :-
	findall(_,(finish(Used),writeln(Used)),_).


allsols2 :-
	findall(_,(setof(Used,finish(Used),Useds),maplist(writeln,Useds)),_).
	

