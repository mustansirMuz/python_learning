# fill in this function
import types
from typing import Generator


def fib() -> Generator[int]:
    a = 1
    b = 1
    yield a
    yield b
    while True:
        yield a + b
        a, b = b, a + b


# testing code
if type(fib()) == types.GeneratorType:
    print("Good, The fib function is a generator.")

    counter = 0
    for n in fib():
        print(n)
        counter += 1
        if counter == 10:
            break
