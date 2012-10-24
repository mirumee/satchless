from django.test import TestCase
from ....pricing.handler import PricingQueue
from ....product.tests import DeadParrot
from ....contrib.pricing.field import ProductFieldGetter
from ....contrib.pricing.cache import PricingCacheHandler

from decimal import Decimal


class Cache(TestCase):
    def setUp(self):
        self.parrot = DeadParrot.objects.create(slug='parrot', species='Parrot')
        self.parrot_a = self.parrot.variants.create(color='white',
                                                    looks_alive=True)
        self.parrot.price = Decimal(10)
        self.parrot_a.price = Decimal(11)
        self.cockatoo = DeadParrot.objects.create(slug='cockatoo',
                                                  species='Cockatoo')
        self.cockatoo_a = self.cockatoo.variants.create(color='white',
                                                        looks_alive=True)
        self.cockatoo.price = Decimal(20)
        self.cockatoo_a.price = Decimal(21)
        self.cached_queue = PricingQueue(PricingCacheHandler(ProductFieldGetter))
        self.non_cached_queue = PricingQueue(ProductFieldGetter)

    def test_variant_price(self):
        p0 = self.non_cached_queue.get_variant_price(self.parrot_a, None)
        p1 = self.cached_queue.get_variant_price(self.parrot_a, None)
        self.assertEqual(p0, p1)

        p0 = self.non_cached_queue.get_variant_price(self.cockatoo_a, None)
        p1 = self.cached_queue.get_variant_price(self.cockatoo_a, None)
        self.assertEqual(p0, p1)

    def test_product_price_range(self):
        p0 = self.non_cached_queue.get_product_price_range(self.parrot)
        p1 = self.cached_queue.get_product_price_range(self.parrot)
        self.assertEqual(p0, p1)

        p0 = self.non_cached_queue.get_product_price_range(self.cockatoo)
        p1 = self.cached_queue.get_product_price_range(self.cockatoo)
        self.assertEqual(p0, p1)
