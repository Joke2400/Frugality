from core.app_funcs import parse_store_data

store_str_1 = ""  # regex should fail completely on this
store_str_2 = "Store Name"
store_str_3 = "1234567890"
store_str_4 = "Store Name 1234567890"
store_str_5 = "1234567890 Store Name"  # regex should fail on the name


def test_parse_store_info_1():
    r = parse_store_data(store_str_1)
    assert r is None


def test_parse_store_info_2():
    r = parse_store_data(store_str_2)
    assert r[0] == "Store Name" and r[1] is None


def test_parse_store_info_3():
    r = parse_store_data(store_str_3)
    assert r[0] is None and r[1] == 1234567890


def test_parse_store_info_4():
    r = parse_store_data(store_str_4)
    assert r[0] == "Store Name" and r[1] == 1234567890


def test_parse_store_info_5():
    r = parse_store_data(store_str_5)
    assert r[0] is None and r[1] == 1234567890
