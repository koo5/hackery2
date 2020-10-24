seq([]) --> [].
seq([E|Es]) --> [E], seq(Es).

seqq([]) --> [].
seqq([Es|Ess]) --> seq(Es), seqq(Ess).


a --> [b].
