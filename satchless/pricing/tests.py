import decimal

from django.test import TestCase

from . import Price, PriceRange, LinearTax

class PriceTest(TestCase):
    def setUp(self):
        self.p1 = Price(10, currency='BTC')
        self.p2 = Price(20, currency='BTC')
        self.p3 = Price(30, currency='USD')

    def test_basics(self):
        self.assert_(self.p1.has_value())
        self.assertEqual(self.p1.net, self.p1.gross)

    def test_adding_non_price_object_fails(self):
        self.assertRaises(TypeError, lambda p: p + 10, self.p1)

    def test_multiplication(self):
        p1 = self.p1 * 5
        self.assertEqual(p1.net, 50)
        self.assertEqual(p1.gross, 50)
        p2 = self.p1 * 5
        self.assertEqual(p1, p2)

    def test_valid_comparison(self):
        self.assertLess(self.p1, self.p2)
        self.assertGreater(self.p2, self.p1)

    def test_invalid_comparison(self):
        self.assertRaises(TypeError, lambda: self.p1 < 3)
        self.assertRaises(ValueError, lambda: self.p1 < self.p3)

    def test_nan(self):
        p = self.p1 * decimal.Decimal('NaN')
        self.assert_(not p.has_value())

    def test_valid_addition(self):
        p = self.p1 + self.p2
        self.assertEqual(p.net, 30)
        self.assertEqual(p.gross, 30)

    def test_invalid_addition(self):
        self.assertRaises(ValueError, lambda: self.p1 + self.p3)

    def test_tax(self):
        tax_name = '2x Tax'
        tax = LinearTax(2, name=tax_name)
        p = self.p1 + tax
        self.assertEqual(p.net, self.p1.net)
        self.assertEqual(p.gross, self.p1.gross*2)
        self.assertEqual(p.currency, self.p1.currency)
        self.assertEqual(p.tax_name, tax_name)

class PriceRangeTest(TestCase):
    def setUp(self):
        self.p1 = Price(10, currency='BTC')
        self.p2 = Price(20, currency='BTC')
        self.p3 = Price(30, currency='BTC')
        self.p4 = Price(40, currency='BTC')
        self.pr1 = PriceRange(self.p1, self.p2)
        self.pr2 = PriceRange(self.p3, self.p4)

    def test_basics(self):
        self.assertEqual(self.pr1.min_price, self.p1)
        self.assertEqual(self.pr1.max_price, self.p2)

    def test_valid_addition(self):
        pr1 = self.pr1 + self.pr2
        self.assertEqual(pr1.min_price, self.p1)
        self.assertEqual(pr1.max_price, self.p4)
        pr2 = self.pr1 + self.p3
        self.assertEqual(pr2.min_price, self.p1)
        self.assertEqual(pr2.max_price, self.p3)
        pr3 = self.pr2 + self.p2
        self.assertEqual(pr3.min_price, self.p2)
        self.assertEqual(pr3.max_price, self.p4)

    def test_invalid_addition(self):
        self.assertRaises(TypeError, lambda: self.pr1 + 10)

    def test_valid_membership(self):
        self.assertTrue(self.p1 in self.pr1)
        self.assertTrue(self.p2 in self.pr1)
        self.assertFalse(self.p3 in self.pr1)

    def test_invalid_membership(self):
        self.assertRaises(TypeError, lambda: 15 in self.pr1)

    def test_replacement(self):
        pr1 = self.pr1.replace(max_price=self.p3)
        self.assertEqual(pr1.min_price, self.p1)
        self.assertEqual(pr1.max_price, self.p3)
        pr2 = self.pr2.replace(min_price=self.p2)
        self.assertEqual(pr2.min_price, self.p2)
        self.assertEqual(pr2.max_price, self.p4)

    def test_tax(self):
        tax_name = '2x Tax'
        tax = LinearTax(2, name=tax_name)
        pr = self.pr1 + tax
        self.assertEqual(pr.min_price.net, self.p1.net)
        self.assertEqual(pr.min_price.gross, self.p1.gross*2)
        self.assertEqual(pr.min_price.currency, self.p1.currency)
        self.assertEqual(pr.min_price.tax_name, tax_name)
        self.assertEqual(pr.max_price.net, self.p2.net)
        self.assertEqual(pr.max_price.gross, self.p2.gross*2)
        self.assertEqual(pr.max_price.currency, self.p2.currency)
        self.assertEqual(pr.max_price.tax_name, tax_name)
