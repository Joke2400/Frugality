from core.app_funcs import get_quantity_from_string


def test_1():
    s = "string 1L string"
    r = get_quantity_from_string(s)
    assert r[0] == 1 and r[1] == "L"

  
def test_2():
    s = "string 2 l string"
    r = get_quantity_from_string(s)
    assert r[0] == 2 and r[1] == "l"


def test_3():
    s = "string 500g string"
    r = get_quantity_from_string(s)
    assert r[0] == 500 and r[1] == "g"


def test_4():
    s = "string 500b string"
    r = get_quantity_from_string(s)
    assert r[0] is None and r[1] is None


def test_5():
    s = "string 500 bla g bla bla"
    r = get_quantity_from_string(s)
    assert r[0] is None and r[1] is None


def test_6():
    s = "string 500 g 500g"
    r = get_quantity_from_string(s)
    assert r[0] == 500 and r[1] == "g"
