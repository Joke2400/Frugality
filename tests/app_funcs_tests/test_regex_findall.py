from core.app_funcs import regex_findall


def test_1():
    s = "string 1L string"
    r = regex_findall(r"(\d+)\s?(l|kg|g)", s)
    assert r[0][0] == "1" and r[0][1] == "L"


def test_2():
    s = "string 2 l string"
    r = regex_findall(r"(\d+)\s?(l|kg|g)", s)
    assert r[0][0] == "2" and r[0][1] == "l"


def test_3():
    s = "string 500g string"
    r = regex_findall(r"(\d+)\s?(l|kg|g)", s)
    assert r[0][0] == "500" and r[0][1] == "g"


def test_4():
    s = "string 500b string"
    r = regex_findall(r"(\d+)\s?(l|kg|g)", s)
    assert r is None


def test_5():
    s = "string bla bla bla"
    r = regex_findall(r"(\d+)\s?(l|kg|g)", s)
    assert r is None


def test_6():
    s = "string 500g 500g"
    r = regex_findall(r"(\d+)\s?(l|kg|g)", s)
    assert (r[0][0] == "500" and r[0][1] == "g"
            and r[1][0] == "500" and r[1][1] == "g")
