:- use_module(library(gui_tracer)).

:- protocol(listp).

:- public(member/2).

:- end_protocol.

:- object(list,
    implements(listp)).


    member(Head, [Head| _]).
    member(Head, [_| Tail]) :-
    	gui_tracer:gtrace,
        member(Head, Tail).

:- end_object.
