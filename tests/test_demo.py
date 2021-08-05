""" Integrated test """
import unittest

import stocklab
from lib import StocklabTestCase

class TestDemo(StocklabTestCase):
    def test_import(self):
        from stocklab.core import bundle
        from stocklab.core.node import Node
        from stocklab.core.crawler import Crawler
        self.assertIsInstance(bundle.get_node('Price'), Node)
        self.assertIsInstance(bundle.get_node('MovingAverage'), Node)
        self.assertIsInstance(bundle.get_crawler('FooCrawler'), Crawler)

    def test_configure(self):
        from stocklab.core.config import get_config
        self.assertIsNone(get_config('somethingNotExist'))
        self.assertIsNotNone(get_config('database'))

    def test_demo(self):
        self.assertEqual(stocklab.eval(
            'MovingAverage.stock:acme.date_idx:1000.window:5'), 1121.0)

if __name__ == '__main__':
    unittest.main()

