from core import parse_query_data
from core.app_classes import AmountData


def test_valid_regex_1():
    a = 1
    s = "Maito Laktoositon 1L"
    r = parse_query_data(a, s)
    assert (isinstance(r, AmountData)
            and r.multiplier == 1
            and r.quantity == 1
            and r.unit == "L")


def test_valid_regex_2():
    a = -1000
    s = "Jauheliha 500g"
    r = parse_query_data(a, s)
    assert (isinstance(r, AmountData)
            and r.multiplier == 100
            and r.quantity == 500
            and r.unit == "g")


def test_valid_regex_3():
    a = -65
    s = "Banaani"
    r = parse_query_data(a, s)
    assert (isinstance(r, AmountData)
            and r.multiplier == 65
            and r.quantity is None
            and r.unit is None)


def test_empty_regex_1():
    a = 3.6
    s = ""
    r = parse_query_data(a, s)
    assert (isinstance(r, AmountData)
            and r.multiplier == 3
            and r.quantity is None
            and r.unit is None)


def test_empty_regex_2():
    a = 1
    s = None
    r = parse_query_data(a, s)
    assert (isinstance(r, AmountData)
            and r.multiplier == 1
            and r.quantity is None
            and r.unit is None)
