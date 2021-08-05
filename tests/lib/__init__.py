import unittest
import importlib

import stocklab

class StocklabTestCase(unittest.TestCase):
    def setUp(self):
        self.setup_bundle()
        self.setup_configure()

    def setup_bundle(self):
        import demo.stocklab_demo
        # In case 'stocklab_demo' was imported by other tests
        importlib.reload(demo.stocklab_demo)

    def setup_configure(self):
        from stocklab import configure
        config_file = 'demo/config.yml'
        configure(config_file)

    def tearDown(self):
        stocklab.reset()
