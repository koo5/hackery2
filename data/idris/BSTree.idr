data BSTree : Type -> Type where
	Empty : Ord elem => BSTree elem
	Node : Ord elem => (left : BSTree elem) -> (val : elem) ->
		(right : BSTree elem) -> BSTree elem

insert : elem -> BSTree elem -> BSTree elem
insert x Empty = Node Empty x Empty
insert x orig@(Node left val right)
	= case compare x val of
	LT => Node (insert x left) val right
	EQ => orig
	GT => Node left val (insert x right)


listToTreeHelper : Ord a => List a -> BSTree a -> BSTree a
listToTreeHelper (x :: xs) tree = listToTreeHelper xs (insert x tree)
listToTreeHelper [] tree = tree



listToTree : Ord a => List a -> BSTree a
listToTree l  = listToTreeHelper l Empty

listToTree : List a -> BSTree a
listToTree [] Empty



