# content of test_sample.py
def func(x):
    return x + 1


def test_answer():
    assert func(3) == 5


def test_main(x=1):
    result = x-x
    assert result == 0, "Result is not 0."