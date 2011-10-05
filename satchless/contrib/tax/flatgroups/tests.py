from decimal import Decimal
from django.test import TestCase
from satchless.contrib.pricing.simpleqty.models import ProductPrice
from satchless.product.tests import DeadParrot
from satchless.pricing import Price, PriceRange
from satchless.pricing.handler import PricingQueue

from . import models

class ParrotTaxTest(TestCase):
    def setUp(self):
        self.macaw = DeadParrot.objects.create(slug='macaw',
                                               species="Hyacinth Macaw")
        self.cockatoo = DeadParrot.objects.create(slug='cockatoo',
                                                  species="White Cockatoo")
        self.macaw_blue_a = self.macaw.variants.create(color='blue',
                                                       sku='M-BL-A',
                                                       looks_alive=True)
        self.macaw_blue_d = self.macaw.variants.create(color='blue',
                                                       sku='M-BL-D',
                                                       looks_alive=False)
        self.cockatoo_white_a = self.cockatoo.variants.create(color='white',
                                                              sku='C-WH-A',
                                                              looks_alive=True)
        self.cockatoo_green_a = self.cockatoo.variants.create(color='green',
                                                              sku='C-GR-A-',
                                                              looks_alive=True)
        macaw_price = ProductPrice.objects.create(product=self.macaw,
                                                  price=Decimal('10.0'))
        macaw_price.offsets.create(variant=self.macaw_blue_a,
                                   price_offset=Decimal('2.0'))
        cockatoo_price = ProductPrice.objects.create(product=self.cockatoo,
                                                     price=Decimal('20.0'))
        cockatoo_price.offsets.create(variant=self.cockatoo_green_a,
                                      price_offset=Decimal('5.0'))
        # create tax groups
        self.vat8 = models.TaxGroup.objects.create(name="VAT 8%", rate=8,
                                                   rate_name="8%")
        self.vat23 = models.TaxGroup.objects.create(name="VAT 23%", rate=23,
                                                    rate_name="23%")
        self.vat8.products.add(self.macaw)
        # set the pricing pipeline
        self.pricing_queue = PricingQueue(
            'satchless.contrib.pricing.simpleqty.SimpleQtyPricingHandler',
            'satchless.contrib.tax.flatgroups.FlatGroupPricingHandler')

    def test_nodefault(self):
        # these have 8% VAT
        self.assertEqual(self.pricing_queue.get_variant_price(self.macaw_blue_d,
                                                   currency='PLN'),
                         Price(10, Decimal('10.80'), currency='PLN'))
        self.assertEqual(self.pricing_queue.get_variant_price(self.macaw_blue_a,
                                                   currency='PLN'),
                         Price(12, Decimal('12.96'), currency='PLN'))
        # while these have no tax group, hence the tax is zero
        self.assertEqual(self.pricing_queue.get_variant_price(self.cockatoo_white_a,
                                                   currency='PLN'),
                         Price(20, 20, currency='PLN'))
        self.assertEqual(self.pricing_queue.get_variant_price(self.cockatoo_green_a,
                                                   currency='PLN'),
                         Price(25, 25, currency='PLN'))
        pr = self.pricing_queue.get_product_price_range(self.cockatoo, currency='PLN')
        self.assertEqual(pr, PriceRange(min_price=Price(20, 20,
                                                        currency='PLN'),
                                        max_price=Price(25, 25,
                                                        currency='PLN')))

    def test_default(self):
        self.vat23.default = True
        self.vat23.save()
        # these have 8% VAT
        self.assertEqual(self.pricing_queue.get_variant_price(self.macaw_blue_d,
                                                   currency='PLN'),
                         Price(10, Decimal('10.80'), currency='PLN'))
        self.assertEqual(self.pricing_queue.get_variant_price(self.macaw_blue_a,
                                                   currency='PLN'),
                         Price(12, Decimal('12.96'), currency='PLN'))
        # while these have default 23% VAT
        self.assertEqual(self.pricing_queue.get_variant_price(self.cockatoo_white_a,
                                                   currency='PLN'),
                         Price(20, Decimal('24.60'), currency='PLN'))
        self.assertEqual(self.pricing_queue.get_variant_price(self.cockatoo_green_a,
                                                   currency='PLN'),
                         Price(25, Decimal('30.75'), currency='PLN'))
        pr = self.pricing_queue.get_product_price_range(self.cockatoo, currency='PLN')
        self.assertEqual(pr, PriceRange(min_price=Price(20, Decimal('24.60'),
                                                        currency='PLN'),
                                        max_price=Price(25, Decimal('30.75'),
                                                        currency='PLN')))
