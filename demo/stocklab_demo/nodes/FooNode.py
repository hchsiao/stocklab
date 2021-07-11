from stocklab.core.node import *
from stocklab.runtime import FooCrawler

class FooNode(Node):
    crawler_entry = FooCrawler.bar
    args = Args(
            target_date = Arg(),
            n = Arg(type=int),
            phase_shift = Arg(oneof=['lead', 'zero', 'lag']),
            )
    schema = Schema(
            date = {'type': 'integer', 'pre_proc': 'date_to_timestamp', 'key': True},
            )

    def evaluate(self, target_date, n, phase_shift):
        return f'{target_date}_{n}_{phase_shift}'
