member_2(_, A, A).
member_2([C|A], B, _) :-
	member_2(A, B, C).

member2(B, [C|A]) :-
	member_2(A, B, C).

