import unittest

import stocklab
from lib import StocklabTestCase

class TestBundle(StocklabTestCase):
    def setUp(self):
        super().setUp()
        from stocklab.node import Node
        class FooNode(Node):
            pass
        self.FooNode = FooNode

    def test_register(self):
        from stocklab.core import bundle
        from stocklab.core.node import Node
        self.assertRaises(Exception, bundle.get_node, 'FooNode')
        bundle.register(self.FooNode)
        self.assertIsInstance(bundle.get_node('FooNode'), Node)
        self.assertRaises(AssertionError, bundle.register, self.FooNode)
        bundle.register(self.FooNode, allow_overwrite=True)

if __name__ == '__main__':
    unittest.main()

