from decimal import Decimal
from django.test import TestCase

from ...product.tests import DeadParrot
from .. import signals
from . import cart_app


class ModelsTestCase(TestCase):

    def setUp(self):
        self.macaw = DeadParrot.objects.create(slug='macaw',
                                               species='Hyacinth Macaw')
        self.cockatoo = DeadParrot.objects.create(slug='cockatoo',
                                                  species='White Cockatoo')
        self.macaw_a = self.macaw.variants.create(looks_alive=True)
        self.macaw_d = self.macaw.variants.create(looks_alive=False)

        self.cockatoo_a = self.cockatoo.variants.create(looks_alive=True)
        self.cockatoo_d = self.cockatoo.variants.create(looks_alive=False)

    def test_replace_quantity_for_non_existing_item(self):
        cart = cart_app.Cart.objects.create()

        qr = cart.replace_item(self.macaw_a, 1)
        self.assertEqual(cart.get_quantity(self.macaw_a), Decimal(1))
        self.assertEqual(Decimal(1), qr.new_quantity)

        qr = cart.replace_item(self.macaw_d, Decimal('2.45'))
        # Dead parrot uses default quantity_quantizer (decimal.Decimal(1))
        self.assertEqual(cart.get_quantity(self.macaw_d), Decimal(2))
        self.assertEqual(2, qr.new_quantity)

        qr = cart.replace_item(self.cockatoo_a, Decimal(2))
        self.assertEqual(cart.get_quantity(self.cockatoo_a), Decimal('2'))
        self.assertEqual(Decimal(2), qr.new_quantity)

        qr = cart.replace_item(self.cockatoo_d, '4.11')
        cart.replace_item(self.cockatoo_d, Decimal('4'))
        self.assertEqual(Decimal(4), qr.new_quantity)

    def test_replace_quantity_for_existing_item(self):
        cart = cart_app.Cart.objects.create()

        qr = cart.replace_item(self.macaw_a, 1)
        self.assertEqual(cart.get_quantity(self.macaw_a), Decimal(1))
        self.assertEqual(Decimal(1), qr.new_quantity)

        qr = cart.replace_item(self.macaw_a, '4.11')
        cart.replace_item(self.macaw_a, Decimal('4'))
        self.assertEqual(Decimal(4), qr.new_quantity)

    def test_add_item_for_non_existing_item(self):
        cart = cart_app.Cart.objects.create()

        qr = cart.add_item(self.macaw_a, 1)
        self.assertEqual(cart.get_quantity(self.macaw_a), Decimal(1))
        self.assertEqual(Decimal(1), qr.new_quantity)

        qr = cart.add_item(self.macaw_d, Decimal('2.45'))
        self.assertEqual(cart.get_quantity(self.macaw_d), Decimal(2))
        self.assertEqual(Decimal(2), qr.new_quantity)

        qr = cart.add_item(self.cockatoo_a, Decimal(2))
        self.assertEqual(cart.get_quantity(self.cockatoo_a), Decimal('2'))
        self.assertEqual(Decimal(2), qr.new_quantity)

        qr = cart.add_item(self.cockatoo_d, '4.11')
        self.assertEqual(cart.get_quantity(self.cockatoo_d), Decimal('4'))
        self.assertEqual(Decimal(4), qr.new_quantity)

    def test_add_item_for_existing_item(self):
        cart = cart_app.Cart.objects.create()

        qr = cart.add_item(self.macaw_a, 1)
        self.assertEqual(cart.get_quantity(self.macaw_a), 1)
        self.assertEqual(Decimal(1), qr.new_quantity)

        qr = cart.add_item(self.macaw_a, '4')
        self.assertEqual(cart.get_quantity(self.macaw_a), 5)
        self.assertEqual(Decimal(5), qr.new_quantity)

    def test_remove_item(self):
        cart = cart_app.Cart.objects.create()

        cart.replace_item(self.macaw_a, 1)
        self.assertEqual(cart.get_quantity(self.macaw_a), Decimal('1'))

        cart.replace_item(self.macaw_a, 0)
        self.assertEqual(cart.get_quantity(self.macaw_a), Decimal(0))

        self.assertFalse(cart.items.exists())

    def test_remove_item_for_non_existing_item(self):
        cart = cart_app.Cart.objects.create()

        cart.replace_item(self.macaw_a, 0)
        self.assertEqual(cart.get_quantity(self.macaw_a), 0)

        self.assertFalse(cart.items.exists())


    def test_signals(self):
        cart = cart_app.Cart.objects.create()

        def modify_qty(sender, instance=None, variant=None, old_quantity=None,
                       new_quantity=None, result=None, **kwargs):
            if variant.product == self.macaw:
                result.append((Decimal('0'), u"Out of stock"))
            elif not variant.looks_alive:
                result.append((Decimal('1'), u"Parrots don't rest in groups"))

        signals.cart_quantity_change_check.connect(modify_qty)

        result = cart.replace_item(self.macaw_a, 10, dry_run=True)
        self.assertEqual((result.new_quantity, result.reason),
                         (0, u"Out of stock"))
        self.assertEqual(0, cart.get_quantity(self.macaw_a))
        result = cart.replace_item(self.macaw_a, 10)
        self.assertEqual((result.new_quantity, result.reason),
                         (0, u"Out of stock"))
        self.assertEqual(0, cart.get_quantity(self.macaw_a))
        result = cart.add_item(self.macaw_a, 10)
        self.assertEqual((result.new_quantity, result.quantity_delta,
                          result.reason),
                         (0, 0, u"Out of stock"))
        self.assertEqual(0, cart.get_quantity(self.macaw_a))
        result = cart.replace_item(self.cockatoo_d, 10, dry_run=True)
        self.assertEqual((result.new_quantity, result.reason),
                         (1, u"Parrots don't rest in groups"))
        self.assertEqual(0, cart.get_quantity(self.cockatoo_d))
        result = cart.replace_item(self.cockatoo_d, 10)
        self.assertEqual((result.new_quantity, result.reason),
                         (1, u"Parrots don't rest in groups"))
        self.assertEqual(1, cart.get_quantity(self.cockatoo_d))
        result = cart.add_item(self.cockatoo_d, 10)
        self.assertEqual((result.new_quantity,
                          result.quantity_delta,
                          result.reason),
                         (1, 0, u"Parrots don't rest in groups"))
        self.assertEqual(1, cart.get_quantity(self.cockatoo_d))

