from typing import Callable


def type_check(correct_type: type) -> Callable:
    # put code here

    def type_checker_dec(func: Callable) -> Callable:

        def actual_type_checker(arg):
            if type(arg) == correct_type:
                return func(arg)
            print("Bad Type")
        return actual_type_checker

    return type_checker_dec


@type_check(int)
def times2(num):
    return num*2


print(times2(2))
times2('Not A Number')


@type_check(str)
def first_letter(word):
    return word[0]


print(first_letter('Hello World'))
first_letter(['Not', 'A', 'String'])
