from django.test import TestCase
from django.db import models

from ....product.tests import Parrot, ParrotVariant
from ....cart.tests import cart_app
from .models import VariantStockLevelMixin


# Models for tests
class StockedDeadParrot(Parrot):
    species = models.CharField(max_length=20)


class StockedDeadParrotVariant(ParrotVariant, VariantStockLevelMixin):
    COLOR_CHOICES = (
        ('blue', 'blue'),
        ('white', 'white'),
        ('red', 'red'),
        ('green', 'green'),
    )
    product = models.ForeignKey(StockedDeadParrot, related_name='variants')
    color = models.CharField(max_length=10, choices=COLOR_CHOICES)
    looks_alive = models.BooleanField()

    class Meta:
        unique_together = ('product', 'color', 'looks_alive')


# Tests
class VariantStockLevelTest(TestCase):
    def setUp(self):
        self.cockatoo = StockedDeadParrot.objects.create(slug='cockatoo', species='White Cockatoo')
        self.cockatoo_white_a = self.cockatoo.variants.create(color='white', looks_alive=True, stock_level=2)

    def test_stocklevels(self):
        cart = cart_app.Cart.objects.create()
        cart.replace_item(self.cockatoo_white_a, 2)
        self.assertEqual(cart.get_quantity(self.cockatoo_white_a), 2)
        cart.add_item(self.cockatoo_white_a, 1)
        self.assertEqual(cart.get_quantity(self.cockatoo_white_a), 2)
