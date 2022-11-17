from core.app_classes import AmountData, ProductList, QueryItem, ProductItem
from .responses import response_1, response_2, response_3, response_4

store_name = "Prisma Olari"
store_id = 542862479
store = (store_name, store_id)

a_1 = AmountData(None, None, 100, "")
q_1 = QueryItem(name="abcdef", store=store,
                category="liha-ja-kasviproteiinit-1", amount=a_1)

a_2 = AmountData(1, "L", 5, "1L")
q_2 = QueryItem(name="Maito Laktoositon 1L", store=store,
                category="maito-munat-ja-rasvat-0", amount=a_2)

a_3 = AmountData(None, None, 3, "")
q_3 = QueryItem(name="213489859829", store=store,
                category=None, amount=a_3)

a_4 = AmountData(None, None, 1, "")
q_4 = QueryItem(name="Ruokakerma", store=store,
                category=None, amount=a_4)


def test_response_1_products():
    pl = ProductList(
        response=response_1,
        query=q_1)
    assert len(pl.products) == 0


def test_response_2_products():
    pl = ProductList(
        response=response_2,
        query=q_1)
    assert len(pl.products) == 10 and type(pl.products[0]) == ProductItem


def test_response_3_products():
    pl = ProductList(
        response=response_3,
        query=q_1)
    assert len(pl.products) == 0


def test_response_4_products():
    pl = ProductList(
        response=response_4,
        query=q_1)
    assert len(pl.products) == 10 and type(pl.products[0]) == ProductItem


def test_response_1_variables():
    pl = ProductList(
        response=response_1,
        query=q_1)
    assert pl.store is store and pl.category == "liha-ja-kasviproteiinit-1"


def test_response_2_variables():
    pl = ProductList(
        response=response_2,
        query=q_2)
    assert pl.store is store and pl.category == "maito-munat-ja-rasvat-0"


def test_response_3_variables():
    pl = ProductList(
        response=response_3,
        query=q_3)
    assert pl.store is store and pl.category is None


def test_response_4_variables():
    pl = ProductList(
        response=response_4,
        query=q_4)
    assert pl.store is store and pl.category is None


def test_filter():
    pl = ProductList(
        response=response_1,
        query=q_1)
    assert pl._filter is None
    pl.set_filter("TEST")
    assert pl._filter == "TEST"
    pl.reset_filter()
    assert pl._filter is None


def test_average_priced_cmp():
    pl = ProductList(
        response=response_2,
        query=q_2)
    p = pl.average_priced_cmp
    assert p.price_per_unit == 1.45 and p.total_price == 7.25 and p.name == "Valio Hyv\u00e4 suomalainen Arki\u00ae Eila\u00ae rasvaton maitojuoma 1 l laktoositon"
    pl = ProductList(
        response=response_4,
        query=q_4)
    p = pl.average_priced_cmp
    print(len(pl.products))
    print(p)
    assert p.price_per_unit == 5.95 and p.total_price == 1.19 and p.name == "Arla Lempi 2dl 22% laktoositon ruokakerma"

def test_highest_priced_cmp():
    pass


def test_lowest_priced_cmp():
    pass


def test_response_1_filtered_products():
    pass


def test_response_2_filtered_products():
    pass


def test_response_3_filtered_products():
    pass


def test_response_4_filtered_products():
    pass


def test_get_filtered_products():
    pass


def test_response_1_parse():
    pass


def test_response_2_parse():
    pass


def test_response_3_parse():
    pass


def test_response_4_parse():
    pass
