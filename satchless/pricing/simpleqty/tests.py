from decimal import Decimal
from django.test import TestCase, Client
from django.db import models
from satchless.cart.models import Cart
from satchless.product.models import ProductAbstract, Variant
from .models import ProductPrice, PriceQtyOverride, VariantPriceOffset

class DeadParrot(ProductAbstract):
    species = models.CharField(max_length=20)

class DeadParrotVariant(Variant):
    product = models.ForeignKey(DeadParrot, related_name='variants')
    color = models.CharField(max_length=10, choices=(
                ('blue', 'blue'), ('white', 'white'), ('red', 'red'), ('green', 'green')))
    looks_alive = models.BooleanField()

    def __unicode__(self):
        "For debugging purposes"
        return u"%s %s %s" % (
                "alive" if self.looks_alive else "resting",
                self.get_color_display(), self.product.slug)

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

    def tearDown(self):
        ProductPrice.objects.all().delete()

    def test_basicprices(self):
        macaw_price = ProductPrice.objects.create(product=self.macaw, price=Decimal('10.0'))
        macaw_price.qty_overrides.create(min_qty=5, price=Decimal('9.0'))
        macaw_price.qty_overrides.create(min_qty=10, price=Decimal('8.0'))
        macaw_price.offsets.create(variant=self.macaw_blue_a, price_offset=Decimal('2.0'))
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
        macaw_price = ProductPrice.objects.create(product=self.macaw, price=Decimal('10.0'))
        macaw_price.offsets.create(variant=self.macaw_blue_a, price_offset=Decimal('2.0'))
        macaw_price.offsets.create(variant=self.macaw_red_d, price_offset=Decimal('3.0'))
        macaw_price.offsets.create(variant=self.macaw_red_a, price_offset=Decimal('6.0'))
        cockatoo_price = ProductPrice.objects.create(product=self.cockatoo, price=Decimal('12.0'))
        cockatoo_price.offsets.create(variant=self.cockatoo_white_d, price_offset=Decimal('-5.0'))
        cockatoo_price.offsets.create(variant=self.cockatoo_green_d, price_offset=Decimal('-8.0'))
        cockatoo_price.offsets.create(variant=self.cockatoo_green_a, price_offset=Decimal('4.0'))
        self.assertEqual(self.macaw.get_unit_price_range(), (Decimal('10.0'), Decimal('16.0')))
        self.assertEqual(self.cockatoo.get_unit_price_range(), (Decimal('4.0'), Decimal('16.0')))

    def test_cartprices(self):
        macaw_price = ProductPrice.objects.create(product=self.macaw,
                price=Decimal('10.0'), qty_mode='product')
        macaw_price.qty_overrides.create(min_qty=9, price=Decimal('9.0'))
        macaw_price.offsets.create(variant=self.macaw_blue_a, price_offset=Decimal('2.0'))
        cart = Cart.objects.create(typ='test')
        cart.set_quantity(self.macaw_blue_a, 4)
        cart.set_quantity(self.macaw_blue_d, 4)
        item_macaw_blue_a = cart.items.get(variant=self.macaw_blue_a)
        item_macaw_blue_d = cart.items.get(variant=self.macaw_blue_d)
        self.assertEqual(item_macaw_blue_a.get_unit_price(), Decimal('12.0'))
        self.assertEqual(item_macaw_blue_d.get_unit_price(), Decimal('10.0'))
        cart.add_quantity(self.macaw_blue_a, 1)
        cart.add_quantity(self.macaw_blue_d, 1)
        item_macaw_blue_a = cart.items.get(variant=self.macaw_blue_a)
        item_macaw_blue_d = cart.items.get(variant=self.macaw_blue_d)

        # cartitem
        self.assertEqual(item_macaw_blue_a.get_unit_price(), Decimal('11.0'))
        # contextless product
        self.assertEqual(self.macaw_blue_a.get_unit_price(), Decimal('12.0'))
        # product in cart context
        self.assertEqual(self.macaw_blue_a.get_unit_price(cart=cart), Decimal('11.0'))

        # cartitem
        self.assertEqual(item_macaw_blue_d.get_unit_price(), Decimal('9.0'))
        # contextless product
        self.assertEqual(self.macaw_blue_d.get_unit_price(), Decimal('10.0'))
        # product in cart context
        self.assertEqual(self.macaw_blue_d.get_unit_price(cart=cart), Decimal('9.0'))
