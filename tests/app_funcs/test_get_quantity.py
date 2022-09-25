from core import get_quantity
from utils import LoggerManager as lgm

logger = lgm.get_logger(name="test")


def test_valid_regex_1():
    s = "Maito Laktoositon 1L"
    r = get_quantity(s)
    assert (r["quantity"] == 1 
            and r["unit"] == "L")

def test_valid_regex_2():
    s = "Jauheliha 500g"
    r = get_quantity(s)
    assert (r["quantity"] == 500 
            and r["unit"] == "g")

def test_valid_regex_3():
    s = "Banaani"
    r = get_quantity(s)
    assert (r["quantity"] == None 
            and r["unit"] == None)

def test_empty_regex_1():
    s = ""
    r = get_quantity(s)
    assert (r["quantity"] == None 
            and r["unit"] == None)

def test_empty_regex_2():
    s = None
    r = get_quantity(s)
    assert (r["quantity"] == None 
            and r["unit"] == None)
