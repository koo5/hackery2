s --> [].
s --> [a], s, [b].

work(L) :- 
	length(L,8),
	phrase(s,L),
	print(L).

%swipl  -g  "work(Z)."  -s le.pl -t halt








\+ memberchk(
