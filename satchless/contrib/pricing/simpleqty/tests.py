from django.db import models
from django.test import TestCase

from ....cart.tests.app import MockCart
from ....pricing import Price
from ....pricing.handler import PricingQueue
from ....product.models import Product, Variant
from . import SimpleQtyPricingHandler
from .models import ProductPriceMixin, VariantPriceOffsetMixin, PriceQtyOverride


class DeadParrot(ProductPriceMixin, Product):

    species = models.CharField(max_length=20)


class DeadParrotVariant(VariantPriceOffsetMixin, Variant):

    product = models.ForeignKey(DeadParrot,
                                related_name='variants')
    looks_alive = models.BooleanField()


class TestPriceQtyOverride(PriceQtyOverride):

    product = models.ForeignKey(DeadParrot,
                                related_name='qty_overrides')


class HandlerTestCase(TestCase):

    def setUp(self):
        self.pricing_queue = PricingQueue(SimpleQtyPricingHandler)

    def test_product_price(self):
        unit_price = 10
        macaw = DeadParrot.objects.create(slug='macaw', price=unit_price,
                                          species="Hyacinth Macaw")
        price_range = self.pricing_queue.get_product_price_range(macaw)
        self.assertEqual(price_range.min_price, Price(unit_price, unit_price))
        self.assertEqual(price_range.max_price, Price(unit_price, unit_price))

    def test_variant_price_qty_override_in_variant_mode(self):
        unit_price = 10
        macaw = DeadParrot.objects.create(slug='macaw', price=unit_price,
                                          species="Hyacinth Macaw")
        macaw_a = macaw.variants.create(looks_alive=True)

        # two price overrides points
        qt_override_1 = macaw.qty_overrides.create(min_qty=3, price=8)
        qt_override_2 = macaw.qty_overrides.create(min_qty=6, price=7)

        price = self.pricing_queue.get_variant_price(macaw_a, quantity=1)
        self.assertEqual(price, Price(unit_price, unit_price))

        # first overrides override should be applied
        price = self.pricing_queue.get_variant_price(macaw_a,
                                                     quantity=qt_override_1.min_qty)
        self.assertEqual(price, Price(qt_override_1.price,
                                      qt_override_1.price))

        # second overrides override should be applied
        price = self.pricing_queue.get_variant_price(macaw_a,
                                                     quantity=qt_override_2.min_qty)
        self.assertEqual(price, Price(qt_override_2.price,
                                      qt_override_2.price))

    def test_variant_price_qty_override_in_product_mode(self):
        unit_price = 10
        macaw = DeadParrot.objects.create(slug='macaw', price=unit_price,
                                          qty_mode='product',
                                          species="Hyacinth Macaw")
        macaw_a = macaw.variants.create(looks_alive=True)
        macaw_d = macaw.variants.create(looks_alive=False)

        cart = MockCart()
        cart_item_a = cart.add_item(macaw_a, 1)
        cart.add_item(macaw_d, 1)

        qt_override_1 = macaw.qty_overrides.create(min_qty=3, price=8)
        qt_override_2 = macaw.qty_overrides.create(min_qty=6, price=7)

        price = self.pricing_queue.get_variant_price(macaw_a, quantity=1,
                                                     cart=cart,
                                                     cartitem=cart_item_a)
        self.assertEqual(price, Price(unit_price, unit_price))

        # because 1 macaw_d variant is in cart:
        #   qt_override_1.min_qty - 1 + 1 = qt_override_1.min_qty
        cart_item_a = cart.replace_item(macaw_a, qt_override_1.min_qty-1)
        price = self.pricing_queue.get_variant_price(macaw_a,
                                                     cart=cart,
                                                     cartitem=cart_item_a)
        self.assertEqual(price, Price(qt_override_1.price,
                                      qt_override_1.price))

        # because 1 macaw_d variant is in cart:
        #   qt_override_2.min_qty - 1 + 1 = qt_override_2.min_qty
        cart_item_a = cart.replace_item(macaw_a, qt_override_2.min_qty-1)
        price = self.pricing_queue.get_variant_price(macaw_a,
                                                     cart=cart,
                                                     cartitem=cart_item_a)
        self.assertEqual(price, Price(qt_override_2.price,
                                      qt_override_2.price))

    def test_variant_price_offset(self):
        unit_price = 10
        macaw = DeadParrot.objects.create(slug='macaw', price=unit_price,
                                          species="Hyacinth Macaw")
        macaw_a = macaw.variants.create(looks_alive=True, price_offset=2)

        price = self.pricing_queue.get_variant_price(macaw_a,
                                                     quantity=1)
        self.assertEqual(price, Price(unit_price + macaw_a.price_offset,
                                      unit_price + macaw_a.price_offset))

    def test_variant_price_offset_with_qty_overrides_in_variant_mode(self):
        unit_price = 10
        macaw = DeadParrot.objects.create(slug='macaw', price=unit_price,
                                          species="Hyacinth Macaw")
        macaw_a = macaw.variants.create(looks_alive=True, price_offset=2)

        # two price overrides points
        qt_override_1 = macaw.qty_overrides.create(min_qty=3, price=8)
        qt_override_2 = macaw.qty_overrides.create(min_qty=6, price=7)

        price = self.pricing_queue.get_variant_price(macaw_a, quantity=1)
        self.assertEqual(price, Price(unit_price + macaw_a.price_offset,
                                      unit_price + macaw_a.price_offset))

        # first overrides override should be applied
        price = self.pricing_queue.get_variant_price(macaw_a,
                                                     quantity=qt_override_1.min_qty)
        self.assertEqual(price, Price(qt_override_1.price + macaw_a.price_offset,
                                      qt_override_1.price + macaw_a.price_offset))

        # second overrides override should be applied
        price = self.pricing_queue.get_variant_price(macaw_a,
                                                     quantity=qt_override_2.min_qty)
        self.assertEqual(price, Price(qt_override_2.price + macaw_a.price_offset,
                                      qt_override_2.price + macaw_a.price_offset))

    def test_variant_price_offset_with_qty_override_in_product_mode(self):
        unit_price = 10
        macaw = DeadParrot.objects.create(slug='macaw', price=unit_price,
                                          qty_mode='product',
                                          species="Hyacinth Macaw")
        macaw_a = macaw.variants.create(looks_alive=True, price_offset=2)
        macaw_d = macaw.variants.create(looks_alive=False)

        cart = MockCart()
        cart_item_a = cart.add_item(macaw_a, 1)
        cart.add_item(macaw_d, 1)

        qt_override_1 = macaw.qty_overrides.create(min_qty=3, price=8)

        # because 1 macaw_d variant is in cart:
        #   qt_override_1.min_qty - 1 + 1 = qt_override_1.min_qty
        cart_item_a = cart.replace_item(macaw_a, qt_override_1.min_qty-1)
        price = self.pricing_queue.get_variant_price(macaw_a,
                                                     cart=cart,
                                                     cartitem=cart_item_a)
        self.assertEqual(price, Price(qt_override_1.price + macaw_a.price_offset,
                                      qt_override_1.price + macaw_a.price_offset))

        # variant without price offset
        price = self.pricing_queue.get_variant_price(macaw_d,
                                                     cart=cart,
                                                     cartitem=cart_item_a)
        self.assertEqual(price, Price(qt_override_1.price,
                                      qt_override_1.price))
