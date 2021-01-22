

:- assert(ddd).

x :-
	/* should fail, because ddd shouldn't actually be asserted if we're just parsing...*/
	ddd(!lalala,!tralala).



:- ['parseme.pl'].
