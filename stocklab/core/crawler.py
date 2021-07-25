from . import StocklabObject

class Crawler(StocklabObject):
    """The base class for stocklab Crawlers."""
    def __init__(self):
        super().__init__()

class CrawlerTrigger(Exception):
    """
    A `Node` will raise this exception when the required data is not locally
    available (e.g. not in the database).  This object will also carry the
    parameters for the corresponding crawler function
    (`Crawler.crawler_entry`).
    """
    def __init__(self, **kwargs):
        super().__init__()
        self.kwargs = kwargs

    def __str__(self):
        # TODO: Expose more information?
        return f'CrawlerTrigger {self.kwargs}'
