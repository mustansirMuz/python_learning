# your code goes here
from typing import Callable


def multiplier_of(number: int) -> Callable[[int], int]:
    def multiply(x: int) -> int:
        return x*number
    return multiply


multiply_with_5 = multiplier_of(5)
print(multiply_with_5(9))
multiply_with_4 = multiplier_of(4)
print(multiply_with_4(10))
