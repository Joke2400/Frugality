from core.app_classes import AmountData, ProductList, QueryItem
from .responses import response_1, response_2, response_3, response_4

store_name = "Prisma Olari"
store_id = 542862479

a = AmountData(None, None, 100, "")
q_1 = QueryItem(name="abcdef", store=(store_name, store_id),
                category="liha-ja-kasviproteiinit-1", amount=a)

a = AmountData(1, "L", 5, "1L")
q_2 = QueryItem(name="Maito Laktoositon 1L", store=(store_name, store_id),
                category="maito-munat-ja-rasvat-0", amount=a)

a = AmountData(None, None, 3, "")
q_3 = QueryItem(name="213489859829", store=(store_name, store_id),
                category=None, amount=a)

a = AmountData(None, None, 1, "")
q_4 = QueryItem(name="Ruokakerma", store=(store_name, store_id),
                category=None, amount=a)


def test_response_1():
    r = response_1
    products = ProductList(
        response=response_1,
        query=q_1)
