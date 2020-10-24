string_literal(string_literal(S)) --> "'", string_literal_body(Codes), {string_codes(S, Codes)}, "'".
string_literal_body([X|XR]) --> string_literal_body_item(X), string_literal_body(XR).
string_literal_body([]) --> [].
string_literal_body_item(X) --> [X], {string_codes("'\\", Z), \+member(X, Z)}.
string_literal_body_item(39) --> [92, 39].
string_literal_body_item(92) --> [92, 92].




command_stub(command_stub(S)) --> "command stub:", string_literal(S).




grammar_declaration(grammar_declaration(Node_identifier, Grammar_properties, Grammar)) --> 
	anything_except(["\n"], Grammar_properties), " grammar for ", node_identifier(Node_identifier), " is ", grammar(Grammar).
%, grammar(Grammar).

anything_except(Disallowed_chars, [X|R]) --> [X], {\+ member(X, Disallowed_chars)}, anything_except(Disallowed_chars, R) .
anything_except(Disallowed_chars, []) --> [], {Disallowed_chars = Disallowed_chars} .
node_identifier(node_identifier(L)) --> string_literal_body(L).



node(Node) --> command_stub(Node).
node(Node) --> grammar_declaration(Node).


grammar_item(S) --> string_literal(S).
grammar_item(S) --> node_identifier(S).



grammar([S]) --> grammar_item(S).
grammar([X]) --> "[", grammar_list_body(X), "]".
grammar_list_body([X]) --> grammar_item(X).
grammar_list_body(X|R) --> grammar_item(X), " ", grammar_list_body(R).


%just a dcg helper
string_phrase(String, Grammar) :-
	string_codes(String, Codes), phrase(Grammar, Codes).
test() :- 
	string_phrase("'\\''", string_literal(Y)), 
	writeln(Y),nl(),
	string_phrase("'\\'\\\\\\' <--- one escaped backslash.\n\\''", string_literal(X)), 
	writeln(X),nl(),
	string_phrase("command stub:'banananana'", node(Node1)),  
	writeln(Node1),nl(),
	string_phrase("yellow, beautiful grammar for banananana is 'BANANA'", node(Node2)),  
	writeln(Node2),nl(),
	string_phrase("yellow, doublebeautiful grammar for banananana is [banananana banananana]", node(Node3)),  
	writeln(Node3),nl(),
	true.
:- debug, writeln("tests:"), findall(dummy, test, _), writeln("success.").




%random notes:
 % http://www.swi-prolog.org/pldoc/man?section=ext-dquotes-motivation
 % https://github.com/dragonwasrobot/learn-prolog-now-exercises/blob/master/chapter-09/practical-session.pl
 % https://github.com/dragonwasrobot/learn-prolog-now-exercises/blob/master/chapter-12/prettyPrinter.pl
 % http://www.swi-prolog.org/pldoc/man?predicate=char_type/2





/*
	json-rpc or rest server?
	gui light, maybe copy&paste, for example, can be done in the gui, more complex operations
	go through the server

	the displayed data is mostly on the server.
*/






