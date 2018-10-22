fizz_buzz(Msg) --> anything, fizz(Msg), anything, buzz, anything.
anything --> [].
anything --> [_], anything.
fizz(Msg) -->
    "fizz",
    {
        format('At fizz we have Msg=~w~n', [Msg])
    }.
buzz -->
    "buzz".
anything(X, "banana").
