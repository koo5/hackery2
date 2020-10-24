extern crate num;
use num::bigint::BigUint;
use std::num::{Zero, One};
use std::mem::replace;

// Calculate large fibonacci numbers.
fn fib(n: uint) -> BigUint {
    let mut f0: BigUint = Zero::zero();
    let mut f1: BigUint = One::one();
    for _ in range(0, n) {
        let f2 = f0 + f1;
        // This is a low cost way of swapping f0 with f1 and f1 with f2.
        f0 = replace(&mut f1, f2);
    }
    f0
}

// This is a very large number.

fn main() {
	println!("fib(1000) = {}", fib(1000));
}


