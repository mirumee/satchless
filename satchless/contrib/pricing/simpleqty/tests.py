from decimal import Decimal

from django.conf import settings
from django.test import TestCase

from satchless.cart.models import Cart
from satchless.pricing import Price, PriceRange
from satchless.pricing.handler import PricingQueue
from satchless.product.tests import DeadParrot
from .models import ProductPrice


class ParrotTest(TestCase):
    TEST_PRICING_HANDLERS = [
        'satchless.contrib.pricing.simpleqty.SimpleQtyPricingHandler',
    ]

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
        self.macaw_red_a = self.macaw.variants.create(color='red',
                                                      sku='M-RD-A',
                                                      looks_alive=True)
        self.macaw_red_d = self.macaw.variants.create(color='red',
                                                      sku='M-RD-D',
                                                      looks_alive=False)
        self.cockatoo_white_a = self.cockatoo.variants.create(color='white',
                                                              sku='C-WH-A',
                                                              looks_alive=True)
        self.cockatoo_white_d = self.cockatoo.variants.create(color='white',
                                                              sku='C-WH-D',
                                                              looks_alive=False)
        self.cockatoo_green_a = self.cockatoo.variants.create(color='green',
                                                              sku='C-GR-A',
                                                              looks_alive=True)
        self.cockatoo_green_d = self.cockatoo.variants.create(color='green',
                                                              sku='C-GR-D',
                                                              looks_alive=False)

        self.original_pricing_handlers = settings.SATCHLESS_PRICING_HANDLERS
        self.pricing_queue = PricingQueue(*self.TEST_PRICING_HANDLERS)

    def tearDown(self):
        ProductPrice.objects.all().delete()
        self.pricing_queue = PricingQueue(*self.TEST_PRICING_HANDLERS)

    def test_price(self):
        p1 = Price(10)
        p2 = Price(10)
        self.assertEqual(p1, p2)
        p1 = Price(10,20)
        p2 = Price(10,20)
        self.assertEqual(p1, p2)
        p1 = Price(10,20)
        p2 = Price(20,10)
        self.assertNotEqual(p1, p2)
        self.assertEqual(p1 + p2, Price(30,30))
        self.assertEqual(p1 * 3, Price(30,60))

    def test_basicprices(self):
        macaw_price = ProductPrice.objects.create(product=self.macaw,
                                                  price=Decimal('10.0'))
        macaw_price.qty_overrides.create(min_qty=5, price=Decimal('9.0'))
        macaw_price.qty_overrides.create(min_qty=10, price=Decimal('8.0'))
        macaw_price.offsets.create(variant=self.macaw_blue_a,
                                   price_offset=Decimal('2.0'))
        self.assertEqual(self.pricing_queue.get_variant_price(self.macaw_blue_d, currency='BTC',
                                           quantity=1),
                         Price(Decimal('10.0'), currency='BTC'))
        self.assertEqual(self.pricing_queue.get_variant_price(self.macaw_blue_d, currency='BTC',
                                           quantity=Decimal('4.9999')),
                         Price(Decimal('10.0'), currency='BTC'))
        self.assertEqual(self.pricing_queue.get_variant_price(self.macaw_blue_d, currency='BTC',
                                           quantity=5),
                         Price(Decimal('9.0'), currency='BTC'))
        self.assertEqual(self.pricing_queue.get_variant_price(self.macaw_blue_d, currency='BTC',
                                           quantity=Decimal('9.9999')),
                         Price(Decimal('9.0'), currency='BTC'))
        self.assertEqual(self.pricing_queue.get_variant_price(self.macaw_blue_d, currency='BTC',
                                           quantity=10),
                         Price(Decimal('8.0'), currency='BTC'))
        self.assertEqual(self.pricing_queue.get_variant_price(self.macaw_blue_d, currency='BTC',
                                           quantity=100),
                         Price(Decimal('8.0'), currency='BTC'))
        self.assertEqual(self.pricing_queue.get_variant_price(self.macaw_blue_a, currency='BTC',
                                           quantity=1),
                         Price(Decimal('12.0'), currency='BTC'))
        self.assertEqual(self.pricing_queue.get_variant_price(self.macaw_blue_a, currency='BTC',
                                           quantity=Decimal('4.9999')),
                         Price(Decimal('12.0'), currency='BTC'))
        self.assertEqual(self.pricing_queue.get_variant_price(self.macaw_blue_a, currency='BTC',
                                           quantity=5),
                         Price(Decimal('11.0'), currency='BTC'))
        self.assertEqual(self.pricing_queue.get_variant_price(self.macaw_blue_a, currency='BTC',
                                           quantity=Decimal('9.9999')),
                         Price(Decimal('11.0'), currency='BTC'))
        self.assertEqual(self.pricing_queue.get_variant_price(self.macaw_blue_a, currency='BTC',
                                           quantity=10),
                         Price(Decimal('10.0'), currency='BTC'))
        self.assertEqual(self.pricing_queue.get_variant_price(self.macaw_blue_a, currency='BTC',
                                           quantity=100),
                         Price(Decimal('10.0'), currency='BTC'))

    def test_basicranges(self):
        macaw_price = ProductPrice.objects.create(product=self.macaw,
                                                  price=Decimal('10.0'))
        macaw_price.offsets.create(variant=self.macaw_blue_a,
                                   price_offset=Decimal('2.0'))
        macaw_price.offsets.create(variant=self.macaw_red_d,
                                   price_offset=Decimal('3.0'))
        macaw_price.offsets.create(variant=self.macaw_red_a,
                                   price_offset=Decimal('6.0'))
        cockatoo_price = ProductPrice.objects.create(product=self.cockatoo,
                                                     price=Decimal('12.0'))
        cockatoo_price.offsets.create(variant=self.cockatoo_white_d,
                                      price_offset=Decimal('-5.0'))
        cockatoo_price.offsets.create(variant=self.cockatoo_green_d,
                                      price_offset=Decimal('-8.0'))
        cockatoo_price.offsets.create(variant=self.cockatoo_green_a,
                                      price_offset=Decimal('4.0'))
        self.assertEqual(self.pricing_queue.get_product_price_range(self.macaw, currency='BTC'),
                        PriceRange(min_price=Price(Decimal('10.0'),
                                                   currency='BTC'),
                                   max_price=Price(Decimal('16.0'),
                                                   currency='BTC')))
        self.assertEqual(self.pricing_queue.get_product_price_range(self.cockatoo, currency='BTC'),
                        PriceRange(min_price=Price(Decimal('4.0'),
                                                   currency='BTC'),
                                   max_price=Price(Decimal('16.0'),
                                                   currency='BTC')))

    def test_cartprices(self):
        macaw_price = ProductPrice.objects.create(product=self.macaw,
                                                  price=Decimal('10.0'),
                                                  qty_mode='product')
        macaw_price.qty_overrides.create(min_qty=9, price=Decimal('9.0'))
        macaw_price.offsets.create(variant=self.macaw_blue_a,
                                   price_offset=Decimal('2.0'))
        cart = Cart.objects.create(typ='test')
        cart.set_quantity(self.macaw_blue_a, 4)
        cart.set_quantity(self.macaw_blue_d, 4)
        item_macaw_blue_a = cart.items.get(variant=self.macaw_blue_a)
        item_macaw_blue_d = cart.items.get(variant=self.macaw_blue_d)

        self.assertEqual(item_macaw_blue_d.get_unit_price(currency='BTC'),
                         Price(Decimal('10.0'), currency='BTC'))
        self.assertEqual(item_macaw_blue_a.get_unit_price(currency='BTC'),
                         Price(Decimal('12.0'), currency='BTC'))
        cart.add_quantity(self.macaw_blue_a, 1)
        cart.add_quantity(self.macaw_blue_d, 1)
        item_macaw_blue_a = cart.items.get(variant=self.macaw_blue_a)
        item_macaw_blue_d = cart.items.get(variant=self.macaw_blue_d)

        macaw_variant = item_macaw_blue_a.variant.get_subtype_instance()
        self.assertEqual(self.pricing_queue.get_variant_price(macaw_variant, currency='BTC',
                                           cart=cart),
                         Price(Decimal('11.0'), currency='BTC'))
        # contextless product
        self.assertEqual(self.pricing_queue.get_variant_price(macaw_variant, currency='BTC'),
                         Price(Decimal('12.0'), currency='BTC'))
