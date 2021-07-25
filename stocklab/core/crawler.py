from . import StocklabObject

class Crawler(StocklabObject):
    def __init__(self):
        super().__init__()

class CrawlerTrigger(Exception):
    def __init__(self, **kwargs):
        super().__init__()
        self.kwargs = kwargs

    def __str__(self):
        # TODO: Expose more information?
        return f'CrawlerTrigger {self.kwargs}'
