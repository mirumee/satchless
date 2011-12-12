from decimal import Decimal
from django.db import models
from django.test import TestCase

from ....pricing import Price, PriceRange
from ....pricing.handler import PricingQueue
from ....product.models import Product, Variant
from ....product.tests.pricing import FiveZlotyPriceHandler
from . import FlatGroupPricingHandler
from .models import TaxGroup, TaxedProductMixin


class TaxedParrot(TaxedProductMixin, Product):
    species = models.CharField(max_length=20)


class ParrotVariant(Variant):
    product = models.ForeignKey(TaxedParrot,
                                related_name='variants')
    looks_alive = models.BooleanField(default=False)


class ParrotTaxTest(TestCase):
    def setUp(self):
        # create tax groups
        self.vat8 = TaxGroup.objects.create(name="VAT 8%", rate=8,
                                            rate_name="8%")
        self.vat20 = TaxGroup.objects.create(name="VAT 20%", rate=20,
                                             rate_name="20%")

        self.macaw = TaxedParrot.objects.create(slug='macaw',
                                                tax_group=self.vat8,
                                                species="Hyacinth Macaw")
        self.cockatoo = TaxedParrot.objects.create(slug='cockatoo',
                                                   species="White Cockatoo")
        self.macaw_a = self.macaw.variants.create(looks_alive=True)
        self.cockatoo_a = self.cockatoo.variants.create(looks_alive=True)

        # set the pricing pipeline
        self.pricing_queue = PricingQueue(FiveZlotyPriceHandler,
                                          FlatGroupPricingHandler)

    def test_nodefault(self):
        # these have 8% VAT
        self.assertEqual(self.pricing_queue.get_variant_price(self.macaw_a,
                                                              currency='PLN'),
                         Price(5, Decimal('5.40'), currency='PLN'))
        pr = self.pricing_queue.get_product_price_range(self.macaw, currency='PLN')
        self.assertEqual(pr, PriceRange(min_price=Price(5, Decimal('5.40'),
                                                        currency='PLN'),
                                        max_price=Price(5, Decimal('5.40'),
                                                        currency='PLN')))
        # while these have no tax group, hence the tax is zero
        self.assertEqual(self.pricing_queue.get_variant_price(self.cockatoo_a,
                                                              currency='PLN'),
                         Price(5, 5, currency='PLN'))
        pr = self.pricing_queue.get_product_price_range(self.cockatoo, currency='PLN')
        self.assertEqual(pr, PriceRange(min_price=Price(5, 5,
                                                        currency='PLN'),
                                        max_price=Price(5, 5,
                                                        currency='PLN')))

    def test_default(self):
        self.vat20.default = True
        self.vat20.save()
        # these have 8% VAT
        self.assertEqual(self.pricing_queue.get_variant_price(self.macaw_a,
                                                   currency='PLN'),
                         Price(5, Decimal('5.40'), currency='PLN'))
        pr = self.pricing_queue.get_product_price_range(self.macaw, currency='PLN')
        self.assertEqual(pr, PriceRange(min_price=Price(5, Decimal('5.40'),
                                                        currency='PLN'),
                                        max_price=Price(5, Decimal('5.40'),
                                                        currency='PLN')))
        # while these have default 20% VAT
        self.assertEqual(self.pricing_queue.get_variant_price(self.cockatoo_a,
                                                   currency='PLN'),
                         Price(5, 6, currency='PLN'))
        pr = self.pricing_queue.get_product_price_range(self.cockatoo, currency='PLN')
        self.assertEqual(pr, PriceRange(min_price=Price(5, 6,
                                                        currency='PLN'),
                                        max_price=Price(5, 6,
                                                        currency='PLN')))
