
radiation :-
        x(S0, S1).

x -->
        constraint([0.3*x1, 0.1*x2] =< 2.7),
        constraint([0.5*x1, 0.5*x2] = 6),
        constraint([0.6*x1, 0.4*x2] >= 6),
        [abc],
        constraint([x2] >= 0).
        