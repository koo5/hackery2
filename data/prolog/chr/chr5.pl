:- use_module(library(chr)).

:- chr_constraint  place/2, banana.

place(_, Dir1), place(_, Dir2) ==> Dir1 = Dir2 | fail. % dont place two things on one wall
place(sofa, n) ==> fail.  % door to kitchen doesn't leave enough space for sofa
place(sofa, s) ==> fail.  % outside door and puja niche don't leave enough space for sofa
place(sofa, X), place(tv, Y) ==> opposite(X,Y).  % demand sofa and tv are on opposite walls
place(desk, n) ==> fail.  % don't place the desk on the north wall, no room.

opposite(n, s).
opposite(s, n).
opposite(e, w).
opposite(w, e).


find_placement :-
    member(Sofa, [n, s, e, w]),
    place(sofa, Sofa),
    member(TV, [n, s, e, w]),
    place(tv, TV),
    member(Desk, [n, s, e, w]),
    place(desk, Desk),
    format('place sofa on ~w, tv on ~w, desk on ~w~n', [Sofa, TV, Desk]).


/* why cant i run the goal like this? */
%:- find_placement.

