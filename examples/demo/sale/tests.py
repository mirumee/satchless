from decimal import Decimal

from django.test import TestCase
from localeurl.models import reverse
from satchless.product.tests.pricing import FiveZlotyPriceHandler
from satchless.pricing import Price, handler
from satchless.util.tests import ViewsTestCase

from products.models import Hat
from categories.app import product_app
from .templatetags.sale_tags import category_in_sale_url
from . import models
from . import SalePricingHandler


class SaleTestCase(TestCase):

    def setUp(self):
        self.pricing_queue = handler.PricingQueue(FiveZlotyPriceHandler,
                                                  SalePricingHandler)

    def test_product_discount(self):
        discount = models.DiscountGroup.objects.create(name="40% discount",
                                                       rate=40,
                                                       rate_name="40% discount")
        hat = Hat.objects.create(name='top hat', slug='top-hat',
                                 price=5)

        variant = hat.variants.create(sku='1')

        discounted_product = Hat.objects.create(name='beret', slug='beret',
                                                price=5, discount=discount)
        discounted_variant = discounted_product.variants.create(sku='2')

        self.assertEqual(self.pricing_queue.get_variant_price(variant,
                                                              currency='PLN'),
                         Price(5, Decimal('5.0'), currency='PLN'))

        self.assertEqual(self.pricing_queue.get_variant_price(discounted_variant,
                                                              currency='PLN'),
                         Price(3, 3, currency='PLN'))


class ViewsTestCase(ViewsTestCase):

    def setUp(self):
        self.discount = models.DiscountGroup.objects.create(name="40% discount",
                                                            rate=40,
                                                            rate_name="40% discount")
        self.category_summer = product_app.Category.objects.create(name='summer', slug='summer')
        self.category_winter = product_app.Category.objects.create(name='winter', slug='winter')
        self.discounted_summer_product = Hat.objects.create(name='sombrero', slug='sombrero',
                                                            price=5, discount=self.discount)
        self.discounted_summer_product.categories.add(self.category_summer)
        self.discounted_summer_product.variants.create(sku='2')

        discounted_winter_product = Hat.objects.create(name='ushanka', slug='ushanka',
                                     price=5, discount=self.discount)
        discounted_winter_product.categories.add(self.category_winter)
        discounted_winter_product.variants.create(sku='3')

        undiscounted_summer_product = Hat.objects.create(name='baseball cap',
                                                         slug='baseball-cap',
                                                         price=5)
        undiscounted_summer_product.categories.add(self.category_summer)
        undiscounted_summer_product.variants.create(sku='4')

    def test_sale_index_view(self):
        response = self._test_GET_status(reverse('sale'))
        self.assertEqual(set(self.discount.products.all()),
                         set(response.context['products']))

    def test_discounted_category_view(self):
        response = self._test_GET_status(category_in_sale_url(self.category_summer))
        self.assertEqual(set([p.get_subtype_instance() for p in response.context['products']]),
                         set([self.discounted_summer_product]))
