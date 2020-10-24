data IsTrue : Type where
	IsTrue1 : true -> IsTrue

codata Holds : (e -> e -> Bool) -> List e -> Type where
	HHH : (fun : (e -> e -> Bool)) -> (xyxs : List e) -> (IsTrue (fun x y)) -> (Holds fun (y :: xs)) -> Holds fun x::y::xs
--	HH  : fun -> (x :: []) -> Holds
	H   : (fun : e -> e -> Bool) -> [] -> Holds fun n

data Sorted : Type where
	SortedList : (l : List e) -> (pred: (e -> e -> Bool)) -> (Holds pred list) -> Sorted

