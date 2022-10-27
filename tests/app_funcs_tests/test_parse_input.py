from core import parse_input
from core.app_classes import AmountData, QueryItem

queries = ["Maito Laktoositon 1L", "Jauheliha 500g", "Banaani", "", "Omena"]
amounts = ["1", "-1000", "1.5", "2", ""]
categories = ["", "liha-ja-kasviproteiinit-1", "hedelmat-ja-vihannekset-1", "", ""]
tup = (queries, amounts, categories)


def test_result_len():
    r = parse_input(data=tup)
    assert len(r) == 4


def test_result_type():
    r = parse_input(data=tup)
    assert (isinstance(r, list)
            and isinstance(r[0], QueryItem)
            and isinstance(r[1], QueryItem)
            and isinstance(r[2], QueryItem)
            and isinstance(r[3], QueryItem))


def test_value_at_inx_0():
    r = parse_input(data=tup)
    a = AmountData(multiplier=1, quantity=1, unit="L", quantity_str="1L")
    assert (r[0].name == "Maito Laktoositon 1L"
            and r[0].amount == a
            and r[0].category is None)


def test_value_at_inx_1():
    r = parse_input(data=tup)
    a = AmountData(multiplier=100, quantity=500, unit="g", quantity_str="500g")
    assert (r[1].name == "Jauheliha 500g"
            and r[1].amount == a
            and r[1].category == "liha-ja-kasviproteiinit-1")


def test_value_at_inx_2():
    r = parse_input(data=tup)
    a = AmountData(multiplier=1, quantity=None, unit=None, quantity_str="")
    assert (r[2].name == "Banaani"
            and r[2].amount == a
            and r[2].category == "hedelmat-ja-vihannekset-1")


def test_value_at_inx_3():
    r = parse_input(data=tup)
    a = AmountData(multiplier=1, quantity=None, unit=None, quantity_str="")
    assert (r[3].name == "Omena"
            and r[3].amount == a
            and r[3].category is None)
