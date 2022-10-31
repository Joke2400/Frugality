from core import parse_query_data
from core.app_classes import AmountData


def test_valid_regex_1():
    a = "1"
    s = "Maito Laktoositon 1L"
    r = parse_query_data(a, s)
    a = AmountData(quantity=1, unit="L", multiplier=1, quantity_str="1L")
    assert r == a


def test_valid_regex_2():
    a = "-1000"
    s = "Jauheliha 500g"
    r = parse_query_data(a, s)
    a = AmountData(quantity=500, unit="g", multiplier=100, quantity_str="500g")
    assert r == a


def test_valid_regex_3():
    a = "-65"
    s = "Banaani"
    r = parse_query_data(a, s)
    a = AmountData(quantity=None, unit=None, multiplier=65, quantity_str="")
    assert r == a


def test_valid_regex_4():
    a = ""
    s = "String 500 kg"
    r = parse_query_data(a, s)
    a = AmountData(quantity=500, unit="kg", multiplier=1, quantity_str="500kg")
    assert r == a


def test_empty_regex_1():
    a = "3.6"
    s = ""
    r = parse_query_data(a, s)
    a = AmountData(quantity=None, unit=None, multiplier=3, quantity_str="")
    assert r == a


def test_empty_regex_2():
    a = "1"
    s = None
    r = parse_query_data(a, s)
    a = AmountData(quantity=None, unit=None, multiplier=1, quantity_str="")
    r == a


def test_empty_regex_3():
    a = "abcd"
    s = ""
    r = parse_query_data(a, s)
    a = AmountData(quantity=None, unit=None, multiplier=1, quantity_str="")
    assert r == a

