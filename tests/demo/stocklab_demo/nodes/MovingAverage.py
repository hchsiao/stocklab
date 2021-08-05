from stocklab import DataIdentifier as DI
from stocklab.node import *

class MovingAverage(Node):
    args = Args(
            date_idx = Arg(type=int),
            stock = Arg(),
            window = Arg(type=int),
            )

    def evaluate(date_idx, stock, window, **kwargs):
        dates = range(date_idx - window + 1, date_idx + 1)
        prices = [DI('Price')(stock=stock, date_idx=d) for d in dates]
        return sum(prices)/len(prices)
