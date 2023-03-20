import pytest

@pytest.mark.skip(reason="Used for testing only")
def testFunc(x,y):
    return x+y

def test1():
    assert testFunc(5,10) == 15

def test2():
    assert testFunc(-5,10) == 5

def test3():
    assert testFunc(-5,-5) == -10
