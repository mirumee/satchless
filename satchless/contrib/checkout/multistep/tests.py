# -*- coding: utf-8 -*-
from decimal import Decimal
from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase, Client

from satchless.contrib.delivery.simplepost.models import PostShippingType
from satchless.product.models import Category
from satchless.product.tests import DeadParrot
import satchless.order.handler

from satchless.cart.models import Cart, CART_SESSION_KEY
from satchless.order.models import Order

from ..common.views import prepare_order
from . import views

class CheckoutTest(TestCase):
    def _setup_settings(self, custom_settings):
        original_settings = {}
        for setting_name, value in custom_settings.items():
            if hasattr(settings, setting_name):
                original_settings[setting_name] = getattr(settings, setting_name)
            setattr(settings, setting_name, value)
        return original_settings

    def _teardown_settings(self, original_settings, custom_settings=None):
        custom_settings = custom_settings or {}
        for setting_name, value in custom_settings.items():
            if setting_name in original_settings:
                setattr(settings, setting_name, value)
            else:
                delattr(settings, setting_name)

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

        self.custom_settings = {
            'SATCHLESS_DELIVERY_PROVIDERS': ['satchless.contrib.delivery.simplepost.PostDeliveryProvider'],
            'SATCHLESS_ORDER_PARTITIONERS': ['satchless.contrib.order.partitioner.simple'],
            'SATCHLESS_PAYMENT_PROVIDERS': ['satchless.contrib.payment.django_payments_provider.provider'],
            'SATCHLESS_DJANGO_PAYMENT_TYPES': ['dummy'],
            'PAYMENT_VARIANTS': {'dummy': ('payments.dummy.DummyProvider', {'url': '/', })},
        }
        self.original_settings = self._setup_settings(self.custom_settings)
        satchless.order.handler.init_queues()

        self.anon_client = Client()

        PostShippingType.objects.create(price=12, typ='polecony', name='list polecony')
        PostShippingType.objects.create(price=20, typ='list', name='List zwykly')

    def tearDown(self):
        self._teardown_settings(self.custom_settings, self.original_settings)
        satchless.order.handler.init_queues()

    def _test_status(self, url, method='get', *args, **kwargs):
        status_code = kwargs.pop('status_code', 200)
        client = kwargs.pop('client_instance', Client())
        data = kwargs.pop('data', {})

        response = getattr(client, method)(url, data=data, follow=False)
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

        self._test_status(reverse(prepare_order), method='post',
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

        self._test_status(reverse(prepare_order), method='post',
                          client_instance=self.anon_client, status_code=302)

        order = self._get_order_from_session(self.anon_client.session)
        order_items = self._get_order_items(order)
        # compare cart and order
        self.assertEqual(set(cart.items.values_list('variant', 'quantity')), order_items)

        # update cart
        cart.add_quantity(self.macaw_blue, 100)
        cart.add_quantity(self.macaw_blue_fake, 100)
        self._test_status(reverse(prepare_order), method='post',
                          client_instance=self.anon_client, status_code=302)

        old_order = order
        order = self._get_order_from_session(self.anon_client.session)
        # order should be reused
        self.assertEqual(old_order.pk, order.pk)
        self.assertNotEqual(order, None)
        order_items = self._get_order_items(order)
        # compare cart and order
        self.assertEqual(set(cart.items.values_list('variant', 'quantity')), order_items)

    def _create_cart(self, client):
        cart = self._get_or_create_cart_for_client(client)
        cart.set_quantity(self.macaw_blue, 1)
        cart.set_quantity(self.macaw_blue_fake, Decimal('2.45'))
        cart.set_quantity(self.cockatoo_white_a, Decimal('2.45'))
        return cart

    def _create_order(self, client):
        self._create_cart(client)
        self._test_status(reverse(prepare_order), method='post',
                          client_instance=client, status_code=302)
        return self._get_order_from_session(client.session)

    def test_checkout_view(self):
        order = self._create_order(self.anon_client)
        self._test_status(reverse(views.checkout),
                          client_instance=self.anon_client,
                          status_code=200)
        group = order.groups.get()
        dtypes = satchless.order.handler.get_delivery_types(group)
        dtype = dtypes[0][0]
        data = {
            u'form-0-delivery_type': dtype,
            u'form-MAX_NUM_FORMS': [u''],
            u'form-TOTAL_FORMS': [u'1'],
            u'form-0-id': [u'1'],
            u'form-INITIAL_FORMS': [u'1'],
        }
        self._test_status(reverse(views.checkout), data=data, status_code=302,
                          client_instance=self.anon_client, method='post')
        self.assertEqual(order.groups.get().delivery_type, dtype)

    def test_delivery_details_view(self):
        order = self._create_order(self.anon_client)
        group = order.groups.get()
        dtypes = satchless.order.handler.get_delivery_types(group)
        group.delivery_type = dtypes[0][0]
        group.save()

        self._test_status(reverse(views.delivery_details),
                          client_instance=self.anon_client, method='get')

    def test_delivery_details_view_redirects_to_cart_when_cart_is_missing(self):
        response = self._test_status(reverse(views.delivery_details),
                                     status_code=302, client_instance=self.anon_client, method='get')
        self.assertRedirects(response, reverse('satchless-cart-view'))

    def test_delivery_details_view_redirects_to_checkout_when_delivery_type_is_missing(self):
        self._create_order(self.anon_client)
        self._test_status(reverse(views.delivery_details),
                          status_code=302, client_instance=self.anon_client, method='get')
        #self.assertRedirects(response, reverse(views.checkout))

    def test_payment_view_redirects_to_payment_choice_view_when_payment_type_is_missing(self):
        self._create_order(self.anon_client)
        self._test_status(reverse(views.payment_details),
                          status_code=302, client_instance=self.anon_client, method='get')
        #self.assertRedirects(response, reverse(views.payment_choice))

    #def test_payment_view_redirects_to_payment_choice_view_when_payment_type_is_unknown(self):
    #   pass
