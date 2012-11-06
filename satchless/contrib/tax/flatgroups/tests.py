from decimal import Decimal
from django.db import models
from django.test import TestCase
from prices import Price, PriceRange

from ....product.models import Product, Variant
from .models import TaxGroup, TaxedProductMixin, TaxedVariantMixin


class TaxedParrot(TaxedProductMixin, Product):
    species = models.CharField(max_length=20)


class ParrotVariant(TaxedVariantMixin, Variant):
    product = models.ForeignKey(TaxedParrot,
                                related_name='variants')

    def get_price_per_item(self, **kwargs):
        return Price(5, currency='PLN')


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

    def test_taxed_product_price(self):
        # 8% VAT
        self.assertEqual(self.macaw_variant.get_price(currency='PLN'),
                         Price(5, Decimal('5.40'), currency='PLN'))
        pr = self.macaw.get_price_range(currency='PLN')
        self.assertEqual(pr, PriceRange(min_price=Price(5, Decimal('5.40'),
                                                        currency='PLN'),
                                        max_price=Price(5, Decimal('5.40'),
                                                        currency='PLN')))

    def test_non_taxed_product_price(self):
        # no tax group - tax should be zero
        self.assertEqual(self.cockatoo_variant.get_price(currency='PLN'),
                         Price(5, currency='PLN'))
        pr = self.cockatoo.get_price_range(currency='PLN')
        self.assertEqual(pr, PriceRange(min_price=Price(5, currency='PLN'),
                                        max_price=Price(5, currency='PLN')))
