class ScraperMeta(type):
    """A scraper metaclass"""

    def __instancecheck__(cls, instance):
        return cls.__subclasscheck__(type(instance))

    def __subclasscheck__(cls, subclass):
        return hasattr(subclass, "get_page_source") and callable(
            subclass.get_page_source
        )


class ScraperInterface(metaclass=ScraperMeta):
    def get_page_source(self):
        print("From Interface")
