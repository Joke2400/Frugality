from .foodie_selectors import (
    ProductListSelectors as PLS,
    ProductPageSelectors as PPS,
    StoreListSelectors as SLS
)
from .basic_page_classes import Element


class TopmenuElement(Element):
    """A custom page element class for www.foodie.fi.

    TopmenuElement contains data relating to the currently
    selected store on the page.

    Usage:
        The __init__ scrapes the page with predefined selectors.
        The instance attributes may then be accessed normally.
    """

    def __init__(self, source, xpath):
        super().__init__(source, xpath)
        self.store_display_name = self.extract(
            xpath=PPS.STORE_NAME).strip()
        self.store_name = self.store_display_name.lower()

        self.store_href = self.extract(xpath=PPS.STORE_HREF)
        self.store_address = self.extract(xpath=PPS.STORE_ADDRESS)
        self.store_open_times = self.extract(xpath=PPS.STORE_OPEN_TIMES)


class NavigationElement(Element):
    """A custom page element class for www.foodie.fi.

    NavigationElement contains the next_page and prev_page
    hrefs used for navigation through the store list.

    Usage:
        The __init__ scrapes the page with predefined selectors.
        The instance attributes may then be accessed normally.
    """

    def __init__(self, source, xpath):
        super().__init__(source, xpath)
        if self.extract(source=self.selector) is not None:
            self.next = self.extract(xpath=SLS.NAV_NEXT)
            self.prev = self.extract(xpath=SLS.NAV_PREV)
            self.source.next_page = self.next
            if self.prev.split("&page")[1] != '':
                self.source.prev_page = self.prev


class StoreElement(Element):
    """A custom page element class for www.foodie.fi.

    A StoreElement contains all relevant product data for
    a singular store in the page store list.

    Usage:
        The __init__ scrapes the page with predefined selectors.
        The instance attributes may then be accessed normally.
    """

    def __init__(self, page, selector):
        super().__init__(page, selector)
        self.store_display_name = self.extract(
            xpath=SLS.STORE_NAME).strip()
        self.store_name = self.store_display_name.lower()
        self.store_chain = self.store_name.split(" ")[0]

        self.store_select = self.extract(xpath=SLS.STORE_SELECT)
        self.store_address = self.extract(xpath=SLS.STORE_ADDRESS)
        self.store_open_times = self.extract(xpath=SLS.STORE_OPEN_TIMES)

    def fetch_data(self):
        return {
            "name": self.store_name,
            "chain": self.store_chain,
            "select": self.store_select,
            "address": self.store_address,
            "open_times": self.store_open_times,
            "display_name": self.store_display_name
        }


class ProductElement(Element):
    """A custom page element class for www.foodie.fi.

    A ProductElement contains all relevant product data for
    a singular product in the page product list.

    Usage:
        The __init__ scrapes the page with predefined selectors.
        The instance attributes may then be accessed normally.
    """

    def __init__(self, page, selector):
        super().__init__(page, selector)
        self.price_decimal = self.extract(xpath=PLS.PRODUCT_PRICE_DECIMAL)
        self.display_name = self.extract(xpath=PLS.PRODUCT_NAME).strip()
        self.price_whole = self.extract(xpath=PLS.PRODUCT_PRICE_WHOLE)
        self.unit_price = self.extract(xpath=PLS.PRODUCT_UNIT_PRICE)
        self.shelf_name = self.extract(xpath=PLS.PRODUCT_SHELF_NAME)
        self.shelf_href = self.extract(xpath=PLS.PRODUCT_SHELF_HREF)
        self.quantity = self.extract(xpath=PLS.PRODUCT_QUANTITY)
        self.subname = self.extract(xpath=PLS.PRODUCT_SUBNAME)
        self.unit = self.extract(xpath=PLS.PRODUCT_UNIT)
        self.ean = self.extract(xpath=PLS.PRODUCT_EAN)
        self.img = self.extract(xpath=PLS.PRODUCT_IMG)

        self.product_name = self.display_name.lower()
        if self.quantity is not None:
            self.quantity.replace(",", "")
        if self.unit_price is not None:
            self.unit_price.strip()
        if self.ean is not None:
            self.ean = int(self.ean)

        self.price = None
        self.display_price = None

        if self.price_whole is not None and self.price_decimal is not None:
            self.display_price = str(self.price_whole)
            self.display_price += "." + self.price_decimal + "€"
        else:
            if self.price_decimal is not None:
                self.display_price = "0." + self.price_decimal + "€"
            else:
                self.display_price = self.price_whole + "€"

        self.price = float(self.display_price[:-1])

    def get_details(self):
        return {
            "img": self.img,
            "ean": self.ean,
            "unit": self.unit,
            "price": self.price,
            "subname": self.subname,
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "shelf_name": self.shelf_name,
            "shelf_href": self.shelf_href,
            "product_name": self.product_name,
            "display_price": self.display_price
        }
