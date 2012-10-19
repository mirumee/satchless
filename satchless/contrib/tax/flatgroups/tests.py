from decimal import Decimal
from django.db import models
from django.test import TestCase
from prices import Price, PriceRange

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
        self.macaw_variant = self.macaw.variants.create()

        self.cockatoo = TaxedParrot.objects.create(slug='cockatoo',
                                                   species="White Cockatoo")
        self.cockatoo_variant = self.cockatoo.variants.create()

        # set the pricing pipeline
        self.pricing_queue = PricingQueue(FiveZlotyPriceHandler,
                                          FlatGroupPricingHandler)

    def test_taxed_product_price(self):
        # 8% VAT
        self.assertEqual(self.pricing_queue.get_variant_price(self.macaw_variant,
                                                              currency='PLN'),
                         Price(5, Decimal('5.40'), currency='PLN'))
        pr = self.pricing_queue.get_product_price_range(self.macaw, currency='PLN')
        self.assertEqual(pr, PriceRange(min_price=Price(5, Decimal('5.40'),
                                                        currency='PLN'),
                                        max_price=Price(5, Decimal('5.40'),
                                                        currency='PLN')))

    def test_non_taxed_product_price(self):
        # no tax group - tax should be zero
        self.assertEqual(self.pricing_queue.get_variant_price(self.cockatoo_variant,
                                                              currency='PLN'),
                         Price(5, 5, currency='PLN'))
        pr = self.pricing_queue.get_product_price_range(self.cockatoo, currency='PLN')
        self.assertEqual(pr, PriceRange(min_price=Price(5, 5,
                                                        currency='PLN'),
                                        max_price=Price(5, 5,
                                                        currency='PLN')))
