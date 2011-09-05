from django.test import TestCase
from django.db import models
from satchless.product.models import ProductAbstract, Variant
from satchless.cart.models import Cart

from .models import VariantStockLevelMixin, NonConfigurableVariantStockLevelMixin, NonConfigurableProductWithStockLevel

# Models for tests
class StockedDeadParrot(ProductAbstract):
    species = models.CharField(max_length=20)

class StockedDeadParrotVariant(Variant, VariantStockLevelMixin):
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
        
class NonConfigurableStockedDeadParrot(NonConfigurableProductWithStockLevel):
    species = models.CharField(max_length=20)

class NonConfigurableStockedDeadParrotVariant(Variant, NonConfigurableVariantStockLevelMixin):
    product = models.ForeignKey(NonConfigurableStockedDeadParrot, related_name='variants')


# Tests
class VariantStockLevelTest(TestCase):
    
    def setUp(self):
        self.cockatoo = StockedDeadParrot.objects.create(slug='cockatoo', species='White Cockatoo')
        self.cockatoo_white_a = self.cockatoo.variants.create(color='white', looks_alive=True, stock_level=2)
        
    def test_stocklevels(self):
        cart = Cart.objects.create(typ='satchless.test.cart')
        cart.set_quantity(self.cockatoo_white_a, 2)
        self.assertEqual(cart.get_quantity(self.cockatoo_white_a), 2)
        cart.add_quantity(self.cockatoo_white_a, 1)
        self.assertEqual(cart.get_quantity(self.cockatoo_white_a), 2)

class NonConfigurableVariantStockLevelTest(TestCase):
    
    def setUp(self):
        self.cockatoo = NonConfigurableStockedDeadParrot.objects.create(slug='cockatoo', species='White Cockatoo', stock_level=2)

    def test_variant_has_product_stocklevel(self):
        """The single variant of a NonConfigurableProductWithStockLevel"""
        self.assertEqual(self.cockatoo.variants.get().stock_level, 2)
        self.cockatoo.stock_level = 3
        self.cockatoo.save()
        self.assertEqual(self.cockatoo.variants.get().stock_level, 3)
        
    def test_stocklevels(self):
        cart = Cart.objects.create(typ='satchless.test.cart')
        cart.set_quantity(self.cockatoo.variants.get(), 2)
        self.assertEqual(cart.get_quantity(self.cockatoo.variants.get()), 2)
        cart.add_quantity(self.cockatoo.variants.get(), 1)
        self.assertEqual(cart.get_quantity(self.cockatoo.variants.get()), 2)
