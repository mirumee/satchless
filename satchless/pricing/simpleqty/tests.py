from decimal import Decimal
from django.test import TestCase, Client
from django.db import models
from satchless.product.models import ProductAbstract, Variant
from .models import ProductQtyPrice, VariantPriceOffset

class DeadParrot(ProductAbstract):
    species = models.CharField(max_length=20)

class DeadParrotVariant(Variant):
    product = models.ForeignKey(DeadParrot, related_name='variants')
    color = models.CharField(max_length=10, choices=(
                ('blue', 'blue'), ('white', 'white'), ('red', 'red'), ('green', 'green')))
    looks_alive = models.BooleanField()

    class Meta:
        unique_together = ('product', 'color', 'looks_alive')

class ParrotTest(TestCase):
    def setUp(self):
        self.macaw = DeadParrot.objects.create(slug='macaw',
                species="Hyacinth Macaw")
        self.cockatoo = DeadParrot.objects.create(slug='cockatoo',
                species="White Cockatoo")
        self.macaw_blue_a = self.macaw.variants.create(color='blue', looks_alive=True)
        self.macaw_blue_d = self.macaw.variants.create(color='blue', looks_alive=False)
        self.macaw_red_a = self.macaw.variants.create(color='red', looks_alive=True)
        self.macaw_red_d = self.macaw.variants.create(color='red', looks_alive=False)
        self.cockatoo_white_a = self.cockatoo.variants.create(color='white', looks_alive=True)
        self.cockatoo_white_d = self.cockatoo.variants.create(color='white', looks_alive=False)
        self.cockatoo_green_a = self.cockatoo.variants.create(color='green', looks_alive=True)
        self.cockatoo_green_d = self.cockatoo.variants.create(color='green', looks_alive=False)

    def test_basicprices(self):
        self.macaw.productqtyprice_set.create(min_qty=0, price=Decimal('10.0'))
        self.macaw.productqtyprice_set.create(min_qty=5, price=Decimal('9.0'))
        self.macaw.productqtyprice_set.create(min_qty=10, price=Decimal('8.0'))
        self.macaw_blue_a.variantpriceoffset_set.create(price_offset=Decimal('2.0'))
        self.assertEqual(self.macaw_blue_d.get_unit_price(quantity=1), Decimal('10.0'))
        self.assertEqual(self.macaw_blue_d.get_unit_price(quantity=Decimal('4.9999')), Decimal('10.0'))
        self.assertEqual(self.macaw_blue_d.get_unit_price(quantity=5), Decimal('9.0'))
        self.assertEqual(self.macaw_blue_d.get_unit_price(quantity=Decimal('9.9999')), Decimal('9.0'))
        self.assertEqual(self.macaw_blue_d.get_unit_price(quantity=10), Decimal('8.0'))
        self.assertEqual(self.macaw_blue_d.get_unit_price(quantity=100), Decimal('8.0'))
        self.assertEqual(self.macaw_blue_a.get_unit_price(quantity=1), Decimal('12.0'))
        self.assertEqual(self.macaw_blue_a.get_unit_price(quantity=Decimal('4.9999')), Decimal('12.0'))
        self.assertEqual(self.macaw_blue_a.get_unit_price(quantity=5), Decimal('11.0'))
        self.assertEqual(self.macaw_blue_a.get_unit_price(quantity=Decimal('9.9999')), Decimal('11.0'))
        self.assertEqual(self.macaw_blue_a.get_unit_price(quantity=10), Decimal('10.0'))
        self.assertEqual(self.macaw_blue_a.get_unit_price(quantity=100), Decimal('10.0'))

    def test_basicranges(self):
        self.macaw.productqtyprice_set.create(min_qty=0, price=Decimal('10.0'))
        self.macaw_blue_a.variantpriceoffset_set.create(price_offset=Decimal('2.0'))
        self.macaw_red_d.variantpriceoffset_set.create(price_offset=Decimal('3.0'))
        self.macaw_red_a.variantpriceoffset_set.create(price_offset=Decimal('6.0'))
        self.cockatoo.productqtyprice_set.create(min_qty=0, price=Decimal('12.0'))
        self.cockatoo_white_d.variantpriceoffset_set.create(price_offset=Decimal('-5.0'))
        self.cockatoo_green_d.variantpriceoffset_set.create(price_offset=Decimal('-8.0'))
        self.cockatoo_green_a.variantpriceoffset_set.create(price_offset=Decimal('4.0'))
        self.assertEqual(self.macaw.get_unit_price_range(), (Decimal('10.0'), Decimal('16.0')))
        self.assertEqual(self.cockatoo.get_unit_price_range(), (Decimal('4.0'), Decimal('16.0')))
