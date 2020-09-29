data Vect : Nat -> Type -> Type where
  Nil : Vect Z a
  (::) : a -> Vect k a -> Vect (S k) a

exactLength : (len : Nat) -> (input : Vect m a) -> Maybe (Vect len a)
exactLength {m} len input = ?exactLength_rhs


checkEqNat : (num1 : Nat) -> (num2 : Nat) -> Maybe (EqNat num1 num2)
checkEqNat Z Z = ?checkEqNat_rhs_3
checkEqNat Z (S k) = ?checkEqNat_rhs_4
checkEqNat (S k) Z = ?checkEqNat_rhs_1
checkEqNat (S k) (S j) = ?checkEqNat_rhs_5
