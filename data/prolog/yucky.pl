tastes_yucky("XXX").
edible("ZZZ").


:- food(X,Y) = Z, write(Z), nl, tastes_yucky(X), edible(Y), write(Z).

