:- [library(clpq)].
:- ensure_loaded(library(aggregate)).
:- ensure_loaded(library(between)).

tv(Diag,Area,W,H) :- {
	/*H > 0, W > 0, Area > 0, W > H, Diag > W,*/
	
	Diag * Diag = W * W + H * H, W / H = 16 / 9,
	
	Area = W * H
	}.

print_tv(D, Area, W, H) :-
	tv(D, Area, W, H),
	Am is Area * 2.54 * 2.54 / 10000,
	Wcm is W * 2.54,
	Hcm is H * 2.54,
	format('diag(inch):~1f~t~20+ area(m): ~5f~t~20+ W(cm): ~1f~t~20+ H(cm): ~1f~n', [D, Am, Wcm, Hcm]).


:- forall(between(2, 200, D), print_tv(D,_,_,_)).
