import Data.IORef
count :: Int -> IO Int
count n = do {r <- newIORef 0; loop r 1} where
	loop :: IORef Int -> Int -> IO Int
	loop r i	| i > n = readIORef r
			| otherwise = do {	v <- readIORef r;
						writeIORef r (v+i) ;
						loop r (i+1)}

main = do {x <- count 5000000; print (x)}