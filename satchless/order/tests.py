# -*- coding: utf-8 -*-
from decimal import Decimal

from django.core.urlresolvers import reverse
from django.test import TestCase, Client

from satchless.product.tests import DeadParrot
from satchless.cart.models import Cart

from . import models

class OrderTest(TestCase):
    def setUp(self):
        self.macaw = DeadParrot.objects.create(slug='macaw',
                species="Hyacinth Macaw")
        self.cockatoo = DeadParrot.objects.create(slug='cockatoo',
                species="White Cockatoo")
        self.macaw_blue = self.macaw.variants.create(color='blue', looks_alive=False)
        self.macaw_blue_fake = self.macaw.variants.create(color='blue', looks_alive=True)
        self.cockatoo_white_a = self.cockatoo.variants.create(color='white', looks_alive=True)
        self.cockatoo_white_d = self.cockatoo.variants.create(color='white', looks_alive=False)
        self.cockatoo_blue_a = self.cockatoo.variants.create(color='blue', looks_alive=True)
        self.cockatoo_blue_d = self.cockatoo.variants.create(color='blue', looks_alive=False)

        self.anon_client = Client()

    def test_order_is_updated_when_cart_content_changes(self):
        cart = Cart.objects.create(typ='satchless.test_cart')
        cart.set_quantity(self.macaw_blue, 1)

        order = models.Order.objects.get_from_cart(cart)

        cart.set_quantity(self.macaw_blue_fake, Decimal('2.45'))
        cart.set_quantity(self.cockatoo_white_a, Decimal('2.45'))

        order_items = set()
        for group in order.groups.all():
            order_items.update(group.items.values_list('product_variant', 'quantity'))
        self.assertEqual(set(cart.items.values_list('variant', 'quantity')), order_items)

    def test_order_view(self):
        cart = Cart.objects.create(typ='satchless.test_cart')
        cart.set_quantity(self.macaw_blue, 1)
        cart.set_quantity(self.macaw_blue_fake, Decimal('2.45'))
        cart.set_quantity(self.cockatoo_white_a, Decimal('2.45'))

        order = models.Order.objects.get_from_cart(cart)
        response = self.client.get(reverse('satchless-order-view', args=(order.token,)))
        self.assertEqual(response.status_code, 200)
