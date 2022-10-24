from core import parse_query_data
from core.app_classes import AmountTuple


def test_valid_regex_1():
    a = 1
    s = "Maito Laktoositon 1L"
    r = parse_query_data(a, s)
    assert (isinstance(r, AmountTuple)
            and r[0] == 1
            and r[1] == 1
            and r[2] == "L")


def test_valid_regex_2():
    a = -1000
    s = "Jauheliha 500g"
    r = parse_query_data(a, s)
    assert (isinstance(r, AmountTuple)
            and r[0] == 100
            and r[1] == 500
            and r[2] == "g")


def test_valid_regex_3():
    a = -65
    s = "Banaani"
    r = parse_query_data(a, s)
    assert (isinstance(r, AmountTuple)
            and r[0] == 65
            and r[1] is None
            and r[2] is None)


def test_empty_regex_1():
    a = 3.6
    s = ""
    r = parse_query_data(a, s)
    assert (isinstance(r, AmountTuple)
            and r[0] == 3
            and r[1] is None
            and r[2] is None)


def test_empty_regex_2():
    a = 1
    s = None
    r = parse_query_data(a, s)
    assert (isinstance(r, AmountTuple)
            and r[0] == 1
            and r[1] is None
            and r[2] is None)
