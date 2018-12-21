bs(Ind) --> indents(Ind), [].
bs(Ind) --> indents(Ind), "b:\n", bs(Ind).

indents(0) --> [].
indents(I) --> {I > 0, J is I - 1}, "\t", indents(J).

putall([X|R]) :- 
	put(X),
	putall(R).

putall([]).






% phrase(bs(10), X),putall(X).