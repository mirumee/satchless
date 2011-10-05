import decimal
from django.conf import settings
from django.test import TestCase
from django import template
import mock
from satchless.pricing import Price, PriceRange, PricingHandler
from satchless.pricing.handler import PricingQueue

from ..templatetags import product_prices

__all__ = ['BasicHandlerTest', 'PricingTagsTest']

class FiveZlotyPriceHandler(PricingHandler):
    """Dummy base price handler - everything has 5PLN price"""

    def get_variant_price(self, *args, **kwargs):
        return Price(net=5, gross=5, currency=u'PLN')

    def get_product_price_range(self, *args, **kwargs):
        return PriceRange(min_price=Price(net=5, gross=5, currency=u'PLN'),
                          max_price=Price(net=5, gross=5, currency=u'PLN'))

class NinetyPerecentTaxPriceHandler(PricingHandler):
    """Scary price handler - it counts 90% of tax for everything"""

    def _tax(self, price):
        return Price(currency=price.currency, net=price.net,
                     gross=price.gross*decimal.Decimal('1.9'))

    def get_variant_price(self, *args, **kwargs):
        price = kwargs.get('price')
        return self._tax(price)

    def get_product_price_range(self, *args, **kwargs):
        price_range = kwargs.get('price_range')
        return PriceRange(min_price=self._tax(price_range.min_price),
                          max_price=self._tax(price_range.max_price))

class TenPercentDiscountPriceHandler(PricingHandler):
    """Discount all handler"""

    def _discount(self, price):
        return Price(currency=price.currency,
                     net=price.net*decimal.Decimal('0.9'),
                     gross=price.gross*decimal.Decimal('0.9'))

    def get_variant_price(self, *args, **kwargs):
        price = kwargs.pop('price')
        if kwargs.get('discount', True):
            return self._discount(price)
        return price

    def get_product_price_range(self, *args, **kwargs):
        price_range = kwargs.pop('price_range')
        if kwargs.get('discount', True):
            return PriceRange(min_price=self._discount(price_range.min_price),
                              max_price=self._discount(price_range.max_price))
        return price_range

class BasicHandlerTest(TestCase):
    def setUp(self):
        self.pricing_queue = PricingQueue(FiveZlotyPriceHandler,
                                        NinetyPerecentTaxPriceHandler,
                                        TenPercentDiscountPriceHandler)

    def tearDown(self):
        self.pricing_queue = PricingQueue(*settings.SATCHLESS_PRICING_HANDLERS)

    def test_discounted_price(self):
        price = self.pricing_queue.get_variant_price(None, u'PLN', quantity=1,
                                          discount=True)
        self.assertEqual(price,
                         Price(net=5*decimal.Decimal('0.9'),
                               gross=(5 * decimal.Decimal('1.9') *
                                      decimal.Decimal('0.9')),
                               currency=u'PLN'))

    def test_undiscounted_price(self):
        price = self.pricing_queue.get_variant_price(None, u'PLN', quantity=1,
                                          discount=False)
        self.assertEqual(price,
                         Price(net=5,
                               gross=5*decimal.Decimal('1.9'),
                               currency=u'PLN'))

class PricingTagsTest(TestCase):
    def setUp(self):
        self.pricing_queue = PricingQueue(FiveZlotyPriceHandler,
                                        NinetyPerecentTaxPriceHandler,
                                        TenPercentDiscountPriceHandler)

    def test_undiscounted_variant_price_tag_without_asvar(self):
        token = mock.Mock()
        token.split_contents.return_value = ('variant_price', 'product',
                                             'currency=PLN', 'discount=0',
                                             'handler=handler')
        parser = mock.Mock()
        def side_effect(arg):
            return template.Variable(arg)
        parser.compile_filter = mock.Mock(side_effect=side_effect)

        node = product_prices.variant_price(parser, token)

        #testing simple expresion
        self.assertEqual(node.item.var, 'product')
        self.assertEqual(node.kwargs['currency'].var, 'PLN')
        self.assertEqual(node.kwargs['discount'].var, '0')

        context = {'product': 'product', 'PLN': 'PLN', '0': 0, 'handler': self.pricing_queue}
        result = node.render(context)
        self.assertEqual(result,
                         Price(net=5,
                               gross=5*decimal.Decimal('1.9'),
                               currency=u'PLN'))

    def test_discounted_variant_price_tag_without_asvar(self):
        token = mock.Mock()
        token.split_contents.return_value = ('variant_price', 'product',
                                             'currency=PLN',
                                             'handler=handler')
        parser = mock.Mock()
        def side_effect(arg):
            return template.Variable(arg)
        parser.compile_filter = mock.Mock(side_effect=side_effect)

        node = product_prices.variant_price(parser, token)

        #testing simple expresion
        self.assertEqual(node.item.var, 'product')
        self.assertEqual(node.kwargs['currency'].var, 'PLN')

        context = {'product': 'product', 'PLN': 'PLN', '0': 0, 'handler': self.pricing_queue}
        result = node.render(context)
        self.assertEqual(result,
                         Price(net=5*decimal.Decimal('0.9'),
                               gross=(5 * decimal.Decimal('1.9') *
                                      decimal.Decimal('0.9')),
                               currency=u'PLN'))

    def test_variant_price_tag_with_asvar(self):
        token = mock.Mock()
        token.split_contents.return_value = ('variant_price', 'product',
                                             'currency=PLN', 'handler=handler',
                                             'as', 'price')
        parser = mock.Mock()
        def side_effect(arg):
            return template.Variable(arg)
        parser.compile_filter = mock.Mock(side_effect=side_effect)

        node = product_prices.variant_price(parser, token)
        self.assertEqual(node.item.var, 'product')
        self.assertEqual(node.kwargs['currency'].var, 'PLN')
        self.assertEqual(node.asvar, 'price')

        context = {'product': 'product', 'PLN': 'PLN', '0': 0, 'handler': self.pricing_queue}
        node.render(context)
        self.assertEqual(context['price'],
                         Price(net=5*decimal.Decimal('0.9'),
                               gross=(5 * decimal.Decimal('1.9') *
                                      decimal.Decimal('0.9')),
                               currency=u'PLN'))

    def test_undiscounted_product_price_range(self):
        token = mock.Mock()
        token.split_contents.return_value = ('product_price_range', 'product',
                                             'currency=PLN', 'discount=0',
                                             'handler=handler', 'as','price')
        parser = mock.Mock()
        def side_effect(arg):
            return template.Variable(arg)
        parser.compile_filter = mock.Mock(side_effect=side_effect)

        node = product_prices.product_price_range(parser, token)

        context = {'product': 'product', 'PLN': 'PLN', '0': 0, 'handler': self.pricing_queue}
        node.render(context)
        self.assertEqual(context['price'].min_price,
                         Price(net=5, gross=5*decimal.Decimal('1.9'),
                         currency=u'PLN'))
        self.assertEqual(context['price'].max_price,
                         Price(net=5, gross=5*decimal.Decimal('1.9'),
                         currency=u'PLN'))
