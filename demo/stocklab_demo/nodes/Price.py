from stocklab.core.node import *
from stocklab.runtime import FooCrawler

class Price(Node):
    crawler_entry = FooCrawler.bar
    args = Args(
            target_date = Arg(type=int),
            stock = Arg(),
            )
    schema = Schema(
            date = {'type': 'integer', 'pre_proc': 'date_to_timestamp', 'key': True},
            )

    def evaluate(self, target_date, stock):
        return f'{target_date}_{stock}'
