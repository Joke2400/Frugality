from core.app_funcs import regex_get_quantity


def test_1():
    s = "string 1L string"
    r = regex_get_quantity(s)
    assert r[0] == 1 and r[1] == "L"

  
def test_2():
    s = "string 2 l string"
    r = regex_get_quantity(s)
    assert r[0] == 2 and r[1] == "l"


def test_3():
    s = "string 500g string"
    r = regex_get_quantity(s)
    assert r[0] == 500 and r[1] == "g"


def test_4():
    s = "string 500b string"
    r = regex_get_quantity(s)
    assert r[0] is None and r[1] is None


def test_5():
    s = "string 500 bla g bla bla"
    r = regex_get_quantity(s)
    assert r[0] is None and r[1] is None


def test_6():
    s = "string 500 g 500g"
    r = regex_get_quantity(s)
    assert r[0] == 500 and r[1] == "g"
