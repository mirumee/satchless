# -*- coding: utf-8 -*-
from decimal import Decimal
from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase, Client

from satchless.product.models import Category
from satchless.product import handler
from satchless.product.tests import DeadParrot

from satchless.cart.models import Cart, CART_SESSION_KEY
from satchless.order.models import Order

class CheckoutTest(TestCase):
    def setUp(self):
        category = Category.objects.create(name='parrot')
        self.macaw = DeadParrot.objects.create(slug='macaw',
                species="Hyacinth Macaw")
        self.macaw.categories.add(category)
        self.cockatoo = DeadParrot.objects.create(slug='cockatoo',
                species="White Cockatoo")
        self.cockatoo.categories.add(category)
        self.macaw_blue = self.macaw.variants.create(color='blue', looks_alive=False)
        self.macaw_blue_fake = self.macaw.variants.create(color='blue', looks_alive=True)
        self.cockatoo_white_a = self.cockatoo.variants.create(color='white', looks_alive=True)
        self.cockatoo_white_d = self.cockatoo.variants.create(color='white', looks_alive=False)
        self.cockatoo_blue_a = self.cockatoo.variants.create(color='blue', looks_alive=True)
        self.cockatoo_blue_d = self.cockatoo.variants.create(color='blue', looks_alive=False)

        self.original_product_view_handlers = settings.SATCHLESS_PRODUCT_VIEW_HANDLERS
        settings.SATCHLESS_PRODUCT_VIEW_HANDLERS = [
            'satchless.cart.add_to_cart_handler',
        ]
        handler.init_queue()
        self.anon_client = Client()

    def tearDown(self):
        settings.SATCHLESS_PRODUCT_VIEW_HANDLERS = self.original_product_view_handlers
        handler.init_queue()

    def _test_status(self, url, method='get', *args, **kwargs):
        status_code = kwargs.pop('status_code', 200)
        client = kwargs.pop('client_instance', Client())
        data = kwargs.pop('data', {})

        response = getattr(client, method)(url, data=data)
        self.assertEqual(response.status_code, status_code,
            'Incorrect status code for: %s, (%s, %s)! Expected: %s, received: %s. HTML:\n\n%s' % (
                url.decode('utf-8'), args, kwargs, status_code, response.status_code,
                response.content.decode('utf-8')))
        return response

    def _get_or_create_cart_for_client(self, client, typ='satchless_cart'):
        self._test_status(reverse('satchless-cart-view'), client_instance=self.anon_client)
        return Cart.objects.get(pk=self.anon_client.session[CART_SESSION_KEY % typ], typ=typ)

    def _get_order_from_session(self, session):
        order_pk = session.get('satchless_order', None)
        if order_pk:
            return Order.objects.get(pk=order_pk)
        return None

    def _get_order_items(self, order):
        order_items = set()
        for group in order.groups.all():
            order_items.update(group.items.values_list('product_variant', 'quantity'))
        return order_items

    def test_order_from_cart_view_creates_proper_order(self):
        cart = self._get_or_create_cart_for_client(self.anon_client)
        cart.set_quantity(self.macaw_blue, 1)
        cart.set_quantity(self.macaw_blue_fake, Decimal('2.45'))
        cart.set_quantity(self.cockatoo_white_a, Decimal('2.45'))

        self._test_status(reverse('satchless-checkout-prepare-order'), method='post',
                          client_instance=self.anon_client, status_code=302)

        order = self._get_order_from_session(self.anon_client.session)
        self.assertNotEqual(order, None)
        order_items = self._get_order_items(order)
        self.assertEqual(set(cart.items.values_list('variant', 'quantity')), order_items)

    def test_order_is_updated_after_cart_changes(self):
        cart = self._get_or_create_cart_for_client(self.anon_client)

        cart.set_quantity(self.macaw_blue, 1)
        cart.set_quantity(self.macaw_blue_fake, Decimal('2.45'))
        cart.set_quantity(self.cockatoo_white_a, Decimal('2.45'))

        self._test_status(reverse('satchless-checkout-prepare-order'), method='post',
                          client_instance=self.anon_client, status_code=302)

        order = self._get_order_from_session(self.anon_client.session)
        order_items = self._get_order_items(order)
        # compare cart and order
        self.assertEqual(set(cart.items.values_list('variant', 'quantity')), order_items)

        # update cart
        cart.add_quantity(self.macaw_blue, 100)
        cart.add_quantity(self.macaw_blue_fake, 100)
        self._test_status(reverse('satchless-checkout-prepare-order'), method='post',
                          client_instance=self.anon_client, status_code=302)

        old_order = order
        order = self._get_order_from_session(self.anon_client.session)
        # order should be reused
        self.assertEqual(old_order.pk, order.pk)
        self.assertNotEqual(order, None)
        order_items = self._get_order_items(order)
        # compare cart and order
        self.assertEqual(set(cart.items.values_list('variant', 'quantity')), order_items)

