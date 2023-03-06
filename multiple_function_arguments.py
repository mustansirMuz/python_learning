# edit the functions prototype and implementation
def foo(a: int, b: int, c: int, *args) -> int:
    return len(args)


def bar(a: int, b: int, c: int, **kwargs) -> bool:
    return kwargs.get('magicnumber') == 7


# test code
if foo(1, 2, 3, 4) == 1:
    print("Good.")
if foo(1, 2, 3, 4, 5) == 2:
    print("Better.")
if bar(1, 2, 3, magicnumber=6) == False:
    print("Great.")
if bar(1, 2, 3, magicnumber=7) == True:
    print("Awesome!")
