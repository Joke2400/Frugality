from .foodie_selectors import (
    ProductPageSelectors as PPS,
    StoreListSelectors as SLS
)
from .basic_page_classes import Page, ListElement
from .foodie_page_elements import (
    NavigationElement,
    StoreElement,
    ProductElement,
    TopmenuElement
)


class FoodiePage(Page):
    """A custom page class for www.foodie.fi.

    FoodiePage is the base page class used for www.foodie.fi

    Usage:
        The __init__ scrapes the page with predefined selectors.

        FoodiePage contains a 'topmenu' instance variable which
        contains data relating to the currently selected store.
    """

    def __init__(self, response, prev_page=None, next_page=None):
        super().__init__(response, prev_page, next_page)
        self.topmenu = TopmenuElement(
            source=self,
            xpath=PPS.STORES_TOPMENU)


class StoreListPage(FoodiePage):
    """A custom page class for www.foodie.fi.

    StoreListPage scrapes all the relevant scraped
    data after a store search on foodie.fi.

    Usage:
        The __init__ scrapes the page with predefined selectors.

        StoreListPage contains a 'stores' instance variable which
        contains all of the scraped store data in a list consisting of
        StoreElement(s).

        StoreListPage contains a 'navigation' instance variable containing
        a NavigationElement.

        StoreListPage inherits from FoodiePage and thus contains a
        'topmenu' instance variable as well.
    """

    def __init__(self, response, prev_page=None, next_page=None):
        super().__init__(response, prev_page, next_page)
        self.navigation = NavigationElement(
            source=self,
            xpath=SLS.NAVIGATION_BUTTONS)
        self.store_list = ListElement(
            source=self,
            xpath=SLS.STORE_LIST,
            items_xpath=SLS.STORE_LIST_ELEMENTS,
            element_type=StoreElement)
        self.stores = self.store_list.get_list()


class ProductPage(FoodiePage):
    """A custom page class for www.foodie.fi.

    ProductPage scrapes all the relevant scraped
    data after a product search on foodie.fi.

    Usage:
        The __init__ scrapes the page with predefined selectors.

        ProductPage contains a 'products' instance variable which
        contains all of the scraped product data in a list consisting of
        ProductElement(s).

        ProductPage inherits from FoodiePage and thus contains a
        'topmenu' instance variable as well.
    """

    def __init__(self, response, prev_page=None, next_page=None):
        super().__init__(response, prev_page, next_page)
        self.product_list = ListElement(
            source=self,
            xpath=PPS.PRODUCT_LIST,
            items_xpath=PPS.PRODUCT_LIST_ELEMENTS,
            element_type=ProductElement)
        self.products = self.product_list.get_list()

    def print_products(self, limit=5):
        if len(self.products) != 0:
            print("\n")
            for i, product in enumerate(self.products):
                if i > limit:
                    break
                self.print_details(product=product)
        else:
            print(
                "[PRINT_PRODUCTS]: No products were found on page:",
                f"'{self.response.url}'")
        print("\n")

    def print_details(self, product):
        values = product.get_details()

        def xstr(input_str):
            if input_str is None:
                return ""
            return str(input_str)

        name = xstr(values["name"])
        price = xstr(values["price"])
        quantity = xstr(values['quantity'])
        unit_price = xstr(values['unit_price'])

        print(
            f"[Product]: {name : ^70} Price: {price  : <10}",
            f"Quantity: {quantity : <5} Price/Unit: {unit_price : <5}")
