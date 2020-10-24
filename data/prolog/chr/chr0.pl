


:- chr_constraint sugar/0, water/0, tea_bag/0, tea/1.

sugar,tea_bag,water <=> tea(true).
tea_bag,water <=> tea(false).



:- chr_constraint salt/0, salt_water/0, stir/0, time/0, noise/0, vapor/0.     

stir \ salt,water <=> salt_water, noise.
stir <=> true.

salt_water,time <=> vapor,salt.
water,time <=> vapor,true.


:- chr_constraint more_than_3/1.
more_than_3(N) <=>  ground(N) | N > 3.


:- chr_constraint banana.
:- chr_constraint banana/1.
