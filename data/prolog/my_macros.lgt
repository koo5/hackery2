:- object(my_macros,
    implements(expanding)).    % built-in protocol for expanding predicates

    term_expansion(foo(Char), baz(Code)) :-
        char_code(Char, Code). % standard built-in predicate

    goal_expansion(foo(X), baz(X)).

:- end_object.
