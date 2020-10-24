modules(Ind, Breadth, Depth) --> [];  {Breadth2 is Breadth - 1, dif(0, Breadth2)}, module(Ind, Breadth, Depth), modules(Ind, Breadth2, Depth).
module(Ind, Breadth, Depth) --> "module:\n", {Ind2 is Ind + 1}, {Depth2 is Depth - 1, dif(0, Depth2)}, statements(Ind2, Breadth, Depth2).
statements(Ind, Breadth, Depth) --> {Breadth2 is Breadth - 1, dif(0, Breadth2)}, statement(Ind, Breadth, Depth), statements(Ind, Breadth2, Depth); [].
statement(Ind, Breadth, Depth) --> while(Ind, Breadth, Depth).
while(Ind, Breadth, Depth) --> {Depth2 is Depth - 1, dif(0, Depth2)}, indents(Ind), "while true:\n", {Ind2 is Ind + 1}, statements(Ind2, Breadth, Depth2).

indents(0) --> [].
indents(I) --> {I > 0, J is I - 1}, "\t", indents(J).

putall([X|R]) :- 
	put(X),
	putall(R).

putall([]).

% phrase(bs(10), X),putall(X).