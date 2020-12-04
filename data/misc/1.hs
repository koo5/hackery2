f :: (Fractional a) => [(a -> a -> a)] -> (a -> a -> a)
f (x:xs) = x

a=fmap (\x y z -> x + y / z) [37,4,5,6]

b = [(\x y z -> x + y / z) 3, (\x y z -> x + y / z) 4, (\x y z -> x + y / z) 5, (\x y z -> x + y / z) 6]

-- c = (f a) 8 4
c = (a !! 0) 8 4



main = print c


-- main = putStrLn (show( case (fmap (*) (Just 3)) of 
--    Just a -> a 5))

