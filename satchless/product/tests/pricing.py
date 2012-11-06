import decimal
from django.test import TestCase
from django import template
import mock
from prices import Price, LinearTax

from ...item import Item, ItemRange

from ..templatetags import product_prices

__all__ = ['PricingTagsTest']


class MockProduct(Item):

    def get_price(self, discount=True, **kwargs):
        price = Price('5', currency='PLN')
        if discount:
            price *= decimal.Decimal('0.9')
        price += LinearTax('0.9', 'Tax!')
        return price


class MockProductRange(ItemRange):

    def __iter__(self):
        yield MockProduct()


class PricingTagsTest(TestCase):
    def test_undiscounted_variant_price_tag_without_asvar(self):
        token = mock.Mock()
        token.split_contents.return_value = ('variant_price', 'product',
                                             'currency=PLN', 'discount=0')
        parser = mock.Mock()

        def side_effect(arg):
            return template.Variable(arg)

        parser.compile_filter = mock.Mock(side_effect=side_effect)

        node = product_prices.variant_price(parser, token)

        #testing simple expresion
        self.assertEqual(node.item.var, 'product')
        self.assertEqual(node.kwargs['currency'].var, 'PLN')
        self.assertEqual(node.kwargs['discount'].var, '0')

        context = {'product': MockProduct(), 'PLN': 'PLN', '0': 0}
        result = node.render(context)
        self.assertEqual(result,
                         Price(net=5,
                               gross=5 * decimal.Decimal('1.9'),
                               currency=u'PLN'))

    def test_discounted_variant_price_tag_without_asvar(self):
        token = mock.Mock()
        token.split_contents.return_value = ('variant_price', 'product',
                                             'currency=PLN')
        parser = mock.Mock()

        def side_effect(arg):
            return template.Variable(arg)

        parser.compile_filter = mock.Mock(side_effect=side_effect)

        node = product_prices.variant_price(parser, token)

        #testing simple expresion
        self.assertEqual(node.item.var, 'product')
        self.assertEqual(node.kwargs['currency'].var, 'PLN')

        context = {'product': MockProduct(), 'PLN': 'PLN', '0': 0}
        result = node.render(context)
        self.assertEqual(result,
                         Price(net=5 * decimal.Decimal('0.9'),
                               gross=(5 * decimal.Decimal('1.9') *
                                      decimal.Decimal('0.9')),
                               currency=u'PLN'))

    def test_variant_price_tag_with_asvar(self):
        token = mock.Mock()
        token.split_contents.return_value = ('variant_price', 'product',
                                             'currency=PLN', 'as', 'price')
        parser = mock.Mock()

        def side_effect(arg):
            return template.Variable(arg)

        parser.compile_filter = mock.Mock(side_effect=side_effect)

        node = product_prices.variant_price(parser, token)
        self.assertEqual(node.item.var, 'product')
        self.assertEqual(node.kwargs['currency'].var, 'PLN')
        self.assertEqual(node.asvar, 'price')

        context = {'product': MockProduct(), 'PLN': 'PLN'}
        node.render(context)
        self.assertEqual(context['price'],
                         Price(net=5 * decimal.Decimal('0.9'),
                               gross=(5 * decimal.Decimal('1.9') *
                                      decimal.Decimal('0.9')),
                               currency=u'PLN'))

    def test_undiscounted_product_price_range(self):
        token = mock.Mock()
        token.split_contents.return_value = ('product_price_range', 'product',
                                             'currency=PLN', 'discount=0',
                                             'as', 'price')
        parser = mock.Mock()

        def side_effect(arg):
            return template.Variable(arg)

        parser.compile_filter = mock.Mock(side_effect=side_effect)

        node = product_prices.product_price_range(parser, token)

        context = {'product': MockProductRange(), 'PLN': 'PLN', '0': 0}
        node.render(context)
        self.assertEqual(context['price'].min_price,
                         Price(net=5, gross=5 * decimal.Decimal('1.9'),
                         currency=u'PLN'))
        self.assertEqual(context['price'].max_price,
                         Price(net=5, gross=5 * decimal.Decimal('1.9'),
                         currency=u'PLN'))
