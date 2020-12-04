module Main


my_pow : Nat -> Nat -> Nat
my_pow x Z = 1
my_pow x (S k) = mult x (my_pow x k)


z : Nat -> Nat
z = \x => my_pow x 3


main : IO ()
main = do
	putStrLn "Hello, Idris World!"
	putStrLn (cast (z 3))

