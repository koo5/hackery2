
findKey' :: (Eq k) => k -> [(k,v)] -> v  
findKey' k xs = snd $ head $ filter ((== k) . fst) xs

main :: IO()
main = print $ findKey' 5 [(5, 6), (7, 8)]
