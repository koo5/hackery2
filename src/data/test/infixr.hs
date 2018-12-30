import Data.List

data List a = Nil | a :- List a 
    deriving (Eq,  Show, Ord)
infixr 5 :-

a = 1 :- 2 :- Nil


main :: IO()

main = 
    do 
    print 8888888888888888888888888888888888888888888888888888888888888888888888888888888888888
    print a
    
