import decimal

from django.test import TestCase

from . import Price

class PriceTest(TestCase):
    def test_basics(self):
        p1 = Price(10)
        self.assert_(p1.has_value())
        self.assertEqual(p1.net, p1.gross)
        self.assertRaises(TypeError, lambda p: p + 10, p1)
        p2 = p1 * 5
        self.assertEqual(p2.net, 50)
        self.assertEqual(p2.gross, 50)
        p3 = p1 * 5
        self.assertEqual(p2, p3)
        p4 = p1 * decimal.Decimal('NaN')
        self.assert_(not p4.has_value())
        p5 = p2 + p3
        self.assertEqual(p5.net, 100)
        self.assertEqual(p5.gross, 100)

