class ProductPageSelectors:
    ''' A class that contains XPATH selectors for key elements on the search results page.'''

    STORES_TOPMENU          =   "//div[@id='topmenu-stores']"                        
    STORE_NAME              =   "//div[@class='store-name']//b/text()"
    STORE_HREF              =   "//a[@class='dd-item custom-link clearfix']/@href"
    STORE_ADDRESS           =   "//div[@class='store-row row']/div/div[2]/text()"
    STORE_OPEN_TIMES        =   "//div[@class='store-row row']/div/div[3]/text()"

    PRODUCT_LIST            =   "//ul[@class='shelf js-shelf products-shelf clear clearfix']"
    PRODUCT_LIST_ELEMENTS   =   "//li[@class='relative item effect fade-shadow js-shelf-item js-entrylist-item']"
    PRODUCT_HREF_ELEMENT    =   "//a[@class='js-link-item']"
    PRODUCT_DETAILS         =   "//div[@class='info relative clear']"
    PRODUCT_PRICE_DETAILS   =   "//div[@class='price-and-quantity']"

class ProductListSelectors:
    """
    A class that contains selectors for the product details, all of these are for use within the <li> element for the product 
    """

    #Selectors for the product data contained within PRODUCT_DETAILS
    PRODUCT_NAME            =   "//div[@class='name']/text()"
    PRODUCT_EAN             =   "//li/@data-ean"
    PRODUCT_QUANTITY        =   "//span[@class='quantity']/text()"
    PRODUCT_SUBNAME         =   "//span[@class='subname']/text()"
    PRODUCT_SHELF_NAME      =   "//span[@class='indoor-location-name']/text()"
    PRODUCT_SHELF_HREF      =   "//a[@class='indoor-location js-indoor-location']/@href"

    #Selectors for the product data contained within PRODUCT_PRICE_DETAILS
    PRODUCT_PRICE_WHOLE     =   "//div[@class='price-and-quantity']//span[@class='whole-number ']/text()"
    PRODUCT_PRICE_DECIMAL   =   "//div[@class='price-and-quantity']//span[@class='decimal']/text()"
    PRODUCT_UNIT            =   "//div[@class='price-and-quantity']//span[@class='unit']/text()"
    PRODUCT_UNIT_PRICE      =   "//div[@class='price-and-quantity']//div[@class='unit-price clear js-comp-price ']/text()"

    #Selectors for the product data contained within PRODUCT_HREF_ELEMENT
    PRODUCT_IMG             =   "//a[@class='js-link-item']//img[@class='img-responsive']/@src"
    PRODUCT_HREF            =   "//a[@class='js-link-item']/@href"

class StoreListSelectors:

    STORE_LIST              = "//ul[@id='js-search-store-list']"
    STORE_LIST_ELEMENTS     = "//li[@class='store-row relative clearfix js-store-row']"
    STORE_NAME              = "//a[@class='no-underline inline-block']/div[@class='name']/text()"
    STORE_ADDRESS           = "//a[@class='no-underline inline-block']/div[@class='address']/text()"
    STORE_HREF              = "//a[@class='no-underline inline-block']/@href"
    STORE_SELECT            = "//div[@class='inline-block']//div[@class='btn-group btn-group-sm']/a/@href"
    STORE_OPEN_TIMES        = "//div[@class='inline-block']//span[@class='time']/h1/text()"
    NAVIGATION_BUTTONS      = "//ul[@class='pagination pagination-lg']"
    NAV_NEXT                = "//a[@rel='next']/@href"
    NAV_PREV                = "//a[@rel='prev']/@href"
