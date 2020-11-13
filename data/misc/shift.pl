
p :- 
	reset(q,T,C),
	writeln('T:'),
	writeq(T),nl,
	writeln('C:'),
	writeq(C),nl,
	writeln('end').


q :- 
	writeln('before shift'),
	shift('return value'),
	writeln('after shift').
