from django.test import TestCase
from satchless.product.tests import DeadParrot, DeadParrotVariant
from satchless.cart.models import Cart

from . import models

class StockTest(TestCase):
    def setUp(self):
        self.cockatoo = DeadParrot.objects.create(slug='cockatoo',
                species="White Cockatoo")
        self.cockatoo_white_a = self.cockatoo.variants.create(color='white', looks_alive=True)

    def test_stocklevels(self):
        models.StockLevel.objects.create(variant=self.cockatoo_white_a, quantity=2)
        cart = Cart.objects.create(typ='satchless.test_cart')
        cart.set_quantity(self.cockatoo_white_a, 2)
        self.assertEqual(cart.get_quantity(self.cockatoo_white_a), 2)
        cart.add_quantity(self.cockatoo_white_a, 1)
        self.assertEqual(cart.get_quantity(self.cockatoo_white_a), 2)
