list([])     --> [].
list([L|Ls]) --> [L], list(Ls).

concatenation([]) --> [].
concatenation([List|Lists]) -->
        list(List),
        concatenation(Lists).
    