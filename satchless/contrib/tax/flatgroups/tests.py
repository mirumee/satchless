from decimal import Decimal
from django.conf import settings
from django.test import TestCase
from satchless.contrib.pricing.simpleqty.models import ProductPrice
from satchless.product.tests import DeadParrot, DeadParrotVariant
from satchless.pricing import Price, handler

from . import models

class ParrotTaxTest(TestCase):
    def setUp(self):
        self.macaw = DeadParrot.objects.create(slug='macaw',
                species="Hyacinth Macaw")
        self.cockatoo = DeadParrot.objects.create(slug='cockatoo',
                species="White Cockatoo")
        self.macaw_blue_a = self.macaw.variants.create(color='blue', looks_alive=True)
        self.macaw_blue_d = self.macaw.variants.create(color='blue', looks_alive=False)
        self.cockatoo_white_a = self.cockatoo.variants.create(color='white', looks_alive=True)
        self.cockatoo_green_a = self.cockatoo.variants.create(color='green', looks_alive=True)
        macaw_price = ProductPrice.objects.create(product=self.macaw, price=Decimal('10.0'))
        macaw_price.offsets.create(variant=self.macaw_blue_a, price_offset=Decimal('2.0'))
        cockatoo_price = ProductPrice.objects.create(product=self.cockatoo, price=Decimal('20.0'))
        cockatoo_price.offsets.create(variant=self.cockatoo_green_a, price_offset=Decimal('5.0'))
        # create tax groups
        self.vat8 = models.TaxGroup.objects.create(name="VAT 8%", rate=8, rate_name="8%")
        self.vat23 = models.TaxGroup.objects.create(name="VAT 23%", rate=23, rate_name="23%")
        self.vat8.products.add(self.macaw)
        # set the pricing pipeline
        settings.SATCHLESS_PRICING_HANDLERS = [
            'satchless.contrib.pricing.simpleqty.handler',
            'satchless.contrib.tax.flatgroups.handler',
            ]

    def test_nodefault(self):
        # these have 8% VAT
        self.assertEqual(handler.get_variant_price(self.macaw_blue_d), Price(10, Decimal('10.80')))
        self.assertEqual(handler.get_variant_price(self.macaw_blue_a), Price(12, Decimal('12.96')))
        # while these have no tax group, hence the tax is zero
        self.assertEqual(handler.get_variant_price(self.cockatoo_white_a), Price(20, 20))
        self.assertEqual(handler.get_variant_price(self.cockatoo_green_a), Price(25, 25))

    def test_default(self):
        self.vat23.default = True
        self.vat23.save()
        # these have 8% VAT
        self.assertEqual(handler.get_variant_price(self.macaw_blue_d), Price(10, Decimal('10.80')))
        self.assertEqual(handler.get_variant_price(self.macaw_blue_a), Price(12, Decimal('12.96')))
        # while these have default 23% VAT
        self.assertEqual(handler.get_variant_price(self.cockatoo_white_a), Price(20, Decimal('24.60')))
        self.assertEqual(handler.get_variant_price(self.cockatoo_green_a), Price(25, Decimal('30.75')))
