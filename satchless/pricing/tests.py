import decimal

from django.conf import settings
from django.test import TestCase

from . import Price
from . import handler

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

class FiveDolarPriceHandler(object):
    """Dummy base price handler - everything has 5$ price"""
    @staticmethod
    def get_variant_price(*args, **kwargs):
        return Price(net=5, gross=5, currency=u'$')
    @staticmethod
    def get_product_price_range(*args, **kwargs):
        return ( Price(net=5, gross=5, currency=u'$'),
                 Price(net=5, gross=5, currency=u'$') )
    @staticmethod
    def get_cartitem_unit_price(*args, **kwargs):
        return Price(net=5, gross=5, currency=u'$')

class NinetyPerecentTaxPriceHandler(object):
    """Scary price handler - it counts 90% of tax for everything"""
    @staticmethod
    def _tax(price):
        return Price(currency=price.currency, net=price.net,
                    gross=price.gross*decimal.Decimal('1.9'))
    @staticmethod
    def get_variant_price(*args, **kwargs):
        price = kwargs.get('price')
        return NinetyPerecentTaxPriceHandler._tax(price)
    @staticmethod
    def get_product_price_range(*args, **kwargs):
        price_range = kwargs.get('price_range')
        return ( NinetyPerecentTaxPriceHandler._tax(price_range[0]),
                 NinetyPerecentTaxPriceHandler._tax(price_range[1]) )
    @staticmethod
    def get_cartitem_unit_price(*args, **kwargs):
        price = kwargs.get('price')
        return NinetyPerecentTaxPriceHandler._tax(price)

class HandlerTest(TestCase):
    def setUp(self):
        self.original_pricing_handlers = settings.SATCHLESS_PRICING_HANDLERS
        settings.SATCHLESS_PRICING_HANDLERS = [ 'satchless.pricing.tests.FiveDolarPriceHandler',
                                                NinetyPerecentTaxPriceHandler ]
        handler.init_queue()

    def tearDown(self):
        settings.SATCHLESS_PRICING_HANDLERS = self.original_pricing_handlers
        handler.init_queue()

    def test_price_chain(self):
        chain = handler.get_variant_price_chain(None, u'$', quantity=1)
        self.assertEqual(chain['satchless.pricing.tests.FiveDolarPriceHandler'],
                         Price(net=5, gross=5, currency=u'$'))
        self.assertEqual(chain[NinetyPerecentTaxPriceHandler],
                         Price(net=5, gross=5*decimal.Decimal('1.9'), currency=u'$'))

    def test_cartitem_price_chain(self):
        chain = handler.get_cartitem_unit_price_chain(None, u'$', quantity=1)
        self.assertEqual(chain['satchless.pricing.tests.FiveDolarPriceHandler'],
                         Price(net=5, gross=5, currency=u'$'))
        self.assertEqual(chain[NinetyPerecentTaxPriceHandler],
                         Price(net=5, gross=5*decimal.Decimal('1.9'), currency=u'$'))

    def test_range_price_chain(self):
        chain = handler.get_product_price_range_chain(None, u'$', quantity=1)
        self.assertEqual(chain['satchless.pricing.tests.FiveDolarPriceHandler'],
                         ( Price(net=5, gross=5, currency=u'$'),
                           Price(net=5, gross=5, currency=u'$') ))
        self.assertEqual(chain[NinetyPerecentTaxPriceHandler],
                         ( Price(net=5, gross=5*decimal.Decimal('1.9'), currency=u'$'),
                           Price(net=5, gross=5*decimal.Decimal('1.9'), currency=u'$') ))
