from decimal import Decimal
from django.test import TestCase, Client
from django.db import models
from satchless.cart.models import Cart
from satchless.pricing import Price, get_variant_price, get_product_price_range, get_cartitem_unit_price
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

    def test_price(self):
        p1 = Price()
        p2 = Price()
        self.assertEqual(p1, p2)
        p1 = Price(10)
        p2 = Price(10)
        self.assertEqual(p1, p2)

    def test_basicprices(self):
        macaw_price = ProductPrice.objects.create(product=self.macaw, price=Decimal('10.0'))
        macaw_price.qty_overrides.create(min_qty=5, price=Decimal('9.0'))
        macaw_price.qty_overrides.create(min_qty=10, price=Decimal('8.0'))
        macaw_price.offsets.create(variant=self.macaw_blue_a, price_offset=Decimal('2.0'))
        self.assertEqual(get_variant_price(self.macaw_blue_d, quantity=1), Price(Decimal('10.0')))
        self.assertEqual(get_variant_price(self.macaw_blue_d, quantity=Decimal('4.9999')), Price(Decimal('10.0')))
        self.assertEqual(get_variant_price(self.macaw_blue_d, quantity=5), Price(Decimal('9.0')))
        self.assertEqual(get_variant_price(self.macaw_blue_d, quantity=Decimal('9.9999')), Price(Decimal('9.0')))
        self.assertEqual(get_variant_price(self.macaw_blue_d, quantity=10), Price(Decimal('8.0')))
        self.assertEqual(get_variant_price(self.macaw_blue_d, quantity=100), Price(Decimal('8.0')))
        self.assertEqual(get_variant_price(self.macaw_blue_a, quantity=1), Price(Decimal('12.0')))
        self.assertEqual(get_variant_price(self.macaw_blue_a, quantity=Decimal('4.9999')), Price(Decimal('12.0')))
        self.assertEqual(get_variant_price(self.macaw_blue_a, quantity=5), Price(Decimal('11.0')))
        self.assertEqual(get_variant_price(self.macaw_blue_a, quantity=Decimal('9.9999')), Price(Decimal('11.0')))
        self.assertEqual(get_variant_price(self.macaw_blue_a, quantity=10), Price(Decimal('10.0')))
        self.assertEqual(get_variant_price(self.macaw_blue_a, quantity=100), Price(Decimal('10.0')))

    def test_basicranges(self):
        macaw_price = ProductPrice.objects.create(product=self.macaw, price=Decimal('10.0'))
        macaw_price.offsets.create(variant=self.macaw_blue_a, price_offset=Decimal('2.0'))
        macaw_price.offsets.create(variant=self.macaw_red_d, price_offset=Decimal('3.0'))
        macaw_price.offsets.create(variant=self.macaw_red_a, price_offset=Decimal('6.0'))
        cockatoo_price = ProductPrice.objects.create(product=self.cockatoo, price=Decimal('12.0'))
        cockatoo_price.offsets.create(variant=self.cockatoo_white_d, price_offset=Decimal('-5.0'))
        cockatoo_price.offsets.create(variant=self.cockatoo_green_d, price_offset=Decimal('-8.0'))
        cockatoo_price.offsets.create(variant=self.cockatoo_green_a, price_offset=Decimal('4.0'))
        self.assertEqual(get_product_price_range(self.macaw), (Price(Decimal('10.0')), Price(Decimal('16.0'))))
        self.assertEqual(get_product_price_range(self.cockatoo), (Price(Decimal('4.0')), Price(Decimal('16.0'))))

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
        self.assertEqual(get_cartitem_unit_price(item_macaw_blue_a), Price(Decimal('12.0')))
        self.assertEqual(get_cartitem_unit_price(item_macaw_blue_d), Price(Decimal('10.0')))
        cart.add_quantity(self.macaw_blue_a, 1)
        cart.add_quantity(self.macaw_blue_d, 1)
        item_macaw_blue_a = cart.items.get(variant=self.macaw_blue_a)
        item_macaw_blue_d = cart.items.get(variant=self.macaw_blue_d)

        # cartitem
        self.assertEqual(get_cartitem_unit_price(item_macaw_blue_a), Price(Decimal('11.0')))
        # contextless product
        self.assertEqual(get_variant_price(self.macaw_blue_a), Price(Decimal('12.0')))
        # product in cart context
        self.assertEqual(get_variant_price(self.macaw_blue_a, cart=cart), Price(Decimal('11.0')))

        # cartitem
        self.assertEqual(get_cartitem_unit_price(item_macaw_blue_d), Price(Decimal('9.0')))
        # contextless product
        self.assertEqual(get_variant_price(self.macaw_blue_d), Price(Decimal('10.0')))
        # product in cart context
        self.assertEqual(get_variant_price(self.macaw_blue_d, cart=cart), Price(Decimal('9.0')))
