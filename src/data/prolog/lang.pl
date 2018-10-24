string_literal(string_literal(S)) --> "'", string_literal_body(Codes), {string_codes(S, Codes)}, "'".
string_literal_body([X|XR]) --> string_literal_body_item(X), string_literal_body(XR).
string_literal_body([]) --> [].
string_literal_body_item(X) --> [X], {string_codes("'\\", Z), \+member(X, Z)}.
string_literal_body_item(39) --> [92, 39].
string_literal_body_item(92) --> [92, 92].




command_stub(command_stub(S)) --> "command stub:", string_literal(S).




grammar_declaration(grammar_declaration(Node_identifier, Grammar_properties, Grammar)) --> 
	anything_except(["\n"], Grammar_properties), " grammar for ", node_identifier(Node_identifier), " is ", {Grammar = todo}.
%, grammar(Grammar).

anything_except(Disallowed_chars, [X|R]) --> [X], {\+ member(X, Disallowed_chars)}, anything_except(Disallowed_chars, R) .
anything_except(Disallowed_chars, []) --> [], {Disallowed_chars = Disallowed_chars} .
node_identifier(node_identifier(L)) --> string_literal(L).



node(Node) --> command_stub(Node).
node(Node) --> grammar_declaration(Node).


%just a dcg helper
string_phrase(String, Grammar) :-
	string_codes(String, Codes), phrase(Grammar, Codes).
test() :- 
	debug,
	writeln("tests:"),
	string_phrase("'\\''", string_literal(Y)), writeln(Y),
	string_phrase("'\\'\\\\\\' <--- one escaped backslash.\n\\''", string_literal(X)), writeln(X),
	string_phrase("command stub:'banananana'", node(Node1)),  writeln(Node1),
	string_phrase("yellow, beautiful grammar for 'banananana' is ", node(Node2)),  writeln(Node2),
	true.
:- debug.
:- test.


