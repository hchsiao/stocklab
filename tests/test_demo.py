import unittest
import importlib.util

class TestDemo(unittest.TestCase):
    def subtest_import(self):
        from stocklab.core import bundle
        from stocklab.core.node import Node
        from stocklab.core.crawler import Crawler
        self.assertIsInstance(bundle.get_node('Price'), Node)
        self.assertIsInstance(bundle.get_node('MovingAverage'), Node)
        self.assertIsInstance(bundle.get_crawler('FooCrawler'), Crawler)

    def subtest_configure(self):
        from stocklab import configure
        from stocklab.core.config import get_config
        config_file = 'demo/config.yml'
        configure(config_file)
        self.assertIsNone(get_config('somethingNotExist'))
        self.assertIsNotNone(get_config('database'))

    def test_demo(self):
        import stocklab
        import demo.stocklab_demo
        self.subtest_configure()
        self.subtest_import()
        self.assertEqual(stocklab.eval(
            'MovingAverage.stock:acme.date_idx:1000.window:5'), 1121.0)

if __name__ == '__main__':
    unittest.main()

