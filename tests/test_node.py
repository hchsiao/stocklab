import unittest

import stocklab
from lib import StocklabTestCase

class TestNode(StocklabTestCase):
    def setUp(self):
        super().setUp()
        from stocklab.node import Node, Args, Arg
        class FooNode(Node):
            args = Args(
                    a = Arg(),
                    b = Arg(type=int),
                    c = Arg(oneof=['foo', '123']),
                    )
        
            def evaluate(a, b, c):
                return a, b, c

        self.FooNode = FooNode

    def test_arg_type(self):
        from stocklab.core import bundle
        from stocklab.core.node import Node
        bundle.register(self.FooNode, allow_overwrite=True)
        a, b, c = stocklab.eval('FooNode.a:1.b:2.c:123')
        self.assertTrue(type(a) is str)
        self.assertTrue(type(b) is int)
        self.assertTrue(type(c) is str)
        self.assertRaises(
                AssertionError, stocklab.eval, 'FooNode.a:1.b:2.c:321')

if __name__ == '__main__':
    unittest.main()

