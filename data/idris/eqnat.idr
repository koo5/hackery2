sameS : (eq : EqNat k j) -> EqNat (S k) (S j)
checkEqNat : (num1 : Nat) -> (num2 : Nat) -> Maybe (EqNat num1 num2)
checkEqNat Z Z = Just (Same Z)
checkEqNat Z (S k) = Nothing
checkEqNat (S k) Z = Nothing
checkEqNat (S k) (S j) = case checkEqNat k j of
Nothing => Nothing
Just eq => Just (sameS eq)
