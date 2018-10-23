string_literal(string_literal(S)) --> "'", string_literal_body(Codes), {string_codes(S, Codes)}, "'".
string_literal_body([X|XR]) --> string_literal_body_item(X), string_literal_body(XR).
string_literal_body([]) --> [].
string_literal_body_item(X) --> [X], {string_codes("'\\", Z), \+member(X, Z)}.
string_literal_body_item(39) --> [92, 39].
string_literal_body_item(92) --> [92, 92].




node(Node) --> command_stub(Node).
command_stub(command_stub(S)) --> "command stub:", string_literal(S).





string_phrase(String, Grammar) :-
	string_codes(String, Codes), phrase(Grammar, Codes).
test(X) :- 
	string_phrase("'\\''", string_literal(Y)),
	string_phrase("'\\'\\\\\\' <--- one escaped backslash.\n'", string_literal(X)),
	string_phrase("command stub:'banananana'", node(Node)). 
:- test(X).



grammar_declaration(grammar_declaration(Node_identifier, Grammar_properties, Grammar)) --> 
	anything_except(["\n"]), " grammar for ", node_identifier(Node_identifier), " is ", grammar(Grammar).

anything_except(Disallowed_chars) --> [X], {\+ member(X