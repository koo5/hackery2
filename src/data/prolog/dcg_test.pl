list([])     --> [].
list([L|Ls]) --> [L], list(Ls).

concatenation([]) --> [].
concatenation([List|Lists]) -->
        list(List),
        concatenation(Lists).

%pr(context(Id, Period, Entity, Scenario)) -->     

%head --> p,e,s.
head --> body.

/*
	:error_check_goal :eq (
		[: value "make"; comment "needed to make swipl report dcg errors"],
		[: value "halt"])
*/


