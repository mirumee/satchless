from decimal import Decimal
from django.conf import settings
from django.test import TestCase
from satchless.cart.models import Cart
from satchless.contrib.pricing.simpleqty.models import ProductPrice
from satchless.product.tests import DeadParrot, DeadParrotVariant
from satchless.pricing import Price, handler
import satchless.pricing.handler

from . import models

class ParrotDiscountTest(TestCase):
    def setUp(self):
        self.original_currency = settings.SATCHLESS_DEFAULT_CURRENCY
        settings.SATCHLESS_DEFAULT_CURRENCY = 'BTW'
        # set the pricing pipeline
        self.original_pricing_handlers = settings.SATCHLESS_PRICING_HANDLERS
        settings.SATCHLESS_PRICING_HANDLERS = [
            'satchless.contrib.pricing.simpleqty.handler',
            'sale.handler',
        ]

        self.macaw = DeadParrot.objects.create(slug='macaw',
                species="Hyacinth Macaw")
        self.macaw_blue_a = self.macaw.variants.create(color='blue', looks_alive=True)

        self.cockatoo = DeadParrot.objects.create(slug='cockatoo',
                species="White Cockatoo")
        self.cockatoo_white_a = self.cockatoo.variants.create(color='white', looks_alive=True)

        macaw_price = ProductPrice.objects.create(product=self.macaw, price=Decimal('10.0'))
        cockatoo_price = ProductPrice.objects.create(product=self.cockatoo, price=Decimal('20.0'))

        # create discounts groups
        self.discount30 = models.DiscountGroup.objects.create(name="Spring discount", rate=30, rate_name="30%")
        self.discount30.products.add(self.macaw)

    def tearDown(self):
        settings.SATCHLESS_PRICING_HANDLERS = self.original_pricing_handlers
        settings.SATCHLESS_DEFAULT_CURRENCY = self.original_currency

    def test_product_discount(self):
        # these have 30% discount
        self.assertEqual(handler.get_variant_price(self.macaw_blue_a, currency='BTW'),
                         Price(7, Decimal('7.0'), currency='BTW'))
        # while these have no tax group, hence the discount is zero
        self.assertEqual(handler.get_variant_price(self.cockatoo_white_a, currency='BTW'),
                         Price(20, 20, currency='BTW'))

