
class Page:

    def __init__(self, response, prev_page=None, next_page=None):
        self.response = response
        self.url = response.url
        self.prev_page = prev_page
        self.next_page = next_page


class Element:

    def __init__(self, source, xpath):
        self.source = source
        self.xpath = xpath
        self.selector = self.extract_selector(
            source=self.source.response,
            xpath=self.xpath)

    def extract_selector(self, xpath, source=None):
        if source is None:
            source = self.selector
        selector = source.xpath(xpath)
        return selector

    def extract(self, xpath=None, source=None):
        if source is None:
            source = self.selector
        if xpath is not None:
            content = self.extract_selector(
                source=source,
                xpath=xpath).get()
        else:
            content = self.selector.get()
        return content


class ListElement(Element):

    def __init__(self, source, xpath, items_xpath, element_type):
        super().__init__(source, xpath)
        self.items_xpath = items_xpath
        self.element_type = element_type
        self.list_elements = self.extract(
            xpath=self.items_xpath)

    def get_list(self):
        new_list = []
        for selector in self.list_elements:
            element = self.element_type(
                source=self.source,
                selector=selector)
            new_list.append(element)
        return new_list
