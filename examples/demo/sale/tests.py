from decimal import Decimal

import django.db.models
from django.test import TestCase
from satchless.product.models import Product, Variant
from satchless.product.tests.pricing import FiveZlotyPriceHandler
from satchless.pricing import Price, handler

from . import models
from . import SalePricingHandler


class TestProduct(Product):
    discount = django.db.models.ForeignKey(models.DiscountGroup,
                                           related_name='test_products',
                                           null=True)

class TestProductVariant(Variant):
    product = django.db.models.ForeignKey(TestProduct, related_name='variants')


class SaleTestCase(TestCase):
    def setUp(self):
        self.pricing_queue = handler.PricingQueue(FiveZlotyPriceHandler,
                                                  SalePricingHandler)

    def test_product_discount(self):
        discount = models.DiscountGroup.objects.create(name="40% discount",
                                                       rate=40,
                                                       rate_name="40% discount")

        product = TestProduct.objects.create(slug='product')
        variant = product.variants.create()

        discounted_product = TestProduct.objects.create(slug='discounted-product',
                                         discount=discount)
        discounted_variant = discounted_product.variants.create()

        self.assertEqual(self.pricing_queue.get_variant_price(variant,
                                                              currency='PLN'),
                         Price(5, Decimal('5.0'), currency='PLN'))

        self.assertEqual(self.pricing_queue.get_variant_price(discounted_variant,
                                                              currency='PLN'),
                         Price(3, 3, currency='PLN'))

