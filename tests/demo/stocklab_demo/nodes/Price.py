from stocklab.node import *
from stocklab.core.runtime import FooCrawler

class Price(DataNode):
    crawler_entry = FooCrawler.bar
    args = Args(
            date_idx = Arg(type=int),
            stock = Arg(),
            )
    schema = Schema(
            stock = {'key': True},
            date = {'type': 'integer', 'key': True},
            price = {'type': 'integer'},
            note = {},
            )

    def evaluate(date_idx, stock):
        table = Price.db[Price.name]
        query = table.stock == stock
        query &= table.date == date_idx
        retval = Price.db(query).select(limitby=(0, 1))
        if retval:
            return retval[0].price
        else:
            raise CrawlerTrigger(date=date_idx, stock_id=stock)
