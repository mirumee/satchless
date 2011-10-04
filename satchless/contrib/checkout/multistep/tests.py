# -*- coding: utf-8 -*-
from decimal import Decimal
from django.http import HttpResponse, HttpRequest
from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.core.urlresolvers import reverse
from django.test import TestCase, Client

from ....cart.models import Cart, CART_SESSION_KEY
from ....contrib.delivery.simplepost.models import PostShippingType
from ....order import handler as order_handler
from ....order.models import Order
from ....payment import ConfirmationFormNeeded
from ....payment.tests import TestPaymentProvider
from ....product.tests import DeadParrot

from satchless.product.tests.pricing import FiveZlotyPriceHandler
from satchless.pricing import handler

from ..common.decorators import require_order
from ..common.views import prepare_order, reactivate_order
from . import views

urlpatterns = patterns('',
    url(r'^cart/', include('satchless.cart.urls')),
    url(r'^checkout/', include('satchless.contrib.checkout.multistep.urls')),
    url(r'^order/', include('satchless.order.urls')),
)

class TestPaymentProviderWithConfirmation(TestPaymentProvider):
    def confirm(self, order):
        raise ConfirmationFormNeeded(action='http://test.payment.gateway.example.com')


class CheckoutTest(TestCase):
    urls = 'satchless.contrib.checkout.multistep.tests'

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
        self.macaw = DeadParrot.objects.create(slug='macaw',
                species="Hyacinth Macaw")
        self.cockatoo = DeadParrot.objects.create(slug='cockatoo',
                species="White Cockatoo")
        self.macaw_blue = self.macaw.variants.create(color='blue', sku='M-BL-D',
                                                     looks_alive=False)
        self.macaw_blue_fake = self.macaw.variants.create(color='blue',
                                                          sku='M-BL-A',
                                                          looks_alive=True)
        self.cockatoo_white_a = self.cockatoo.variants.create(color='white',
                                                              sku='C-WH-A',
                                                              looks_alive=True)
        self.cockatoo_white_d = self.cockatoo.variants.create(color='white',
                                                              sku='C-WH-D',
                                                              looks_alive=False)
        self.cockatoo_blue_a = self.cockatoo.variants.create(color='blue',
                                                             sku='C-BL-A',
                                                             looks_alive=True)
        self.cockatoo_blue_d = self.cockatoo.variants.create(color='blue',
                                                             sku='C-BL-D',
                                                             looks_alive=False)

        self.custom_settings = {
            'SATCHLESS_DELIVERY_PROVIDERS': ['satchless.contrib.delivery.simplepost.PostDeliveryProvider'],
            'SATCHLESS_ORDER_PARTITIONERS': ['satchless.contrib.order.partitioner.simple'],
            'SATCHLESS_PAYMENT_PROVIDERS': [TestPaymentProviderWithConfirmation],
            'SATCHLESS_DJANGO_PAYMENT_TYPES': ['dummy'],
            'PAYMENT_VARIANTS': {'dummy': ('payments.dummy.DummyProvider', {'url': '/', })},
        }
        self.original_settings = self._setup_settings(self.custom_settings)
        order_handler.init_queues()

        self.anon_client = Client()

        PostShippingType.objects.create(price=12, typ='polecony', name='list polecony')
        PostShippingType.objects.create(price=20, typ='list', name='List zwykly')

        self.original_handlers = settings.SATCHLESS_PRICING_HANDLERS
        handler.pricing_queue = handler.PricingQueue(FiveZlotyPriceHandler)

    def tearDown(self):
        self._teardown_settings(self.original_settings, self.custom_settings)
        order_handler.init_queues()
        handler.pricing_queue = handler.PricingQueue(*self.original_handlers)

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

    def _get_or_create_cart_for_client(self, client=None, typ='satchless_cart'):
        client = client or self.client
        self._test_status(reverse('satchless-cart-view'), client_instance=client)
        return Cart.objects.get(pk=client.session[CART_SESSION_KEY % typ], typ=typ)

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

    def test_prepare_order_creates_order_and_redirects_to_checkout_when_cart_is_not_empty(self):
        cart = self._get_or_create_cart_for_client(self.anon_client)
        cart.set_quantity(self.macaw_blue, 1)
        response = self._test_status(reverse(prepare_order), method='post',
                                     client_instance=self.anon_client, status_code=302)
        order_pk = self.anon_client.session.get('satchless_order', None)
        order = Order.objects.get(pk=order_pk)
        self.assertRedirects(response, reverse(views.checkout,
                                               kwargs={'order_token':
                                                       order.token}))

    def test_prepare_order_redirects_to_cart_when_cart_is_empty(self):
        self._get_or_create_cart_for_client(self.anon_client)
        response = self._test_status(reverse(prepare_order), method='post',
                                     client_instance=self.anon_client, status_code=302)
        # 'satchless_cart' is taken from multistep/urls.py:
        # url(r'^prepare-order/$', prepare_order, {'typ': 'satchless_cart'}...)
        self.assertRedirects(response, reverse('satchless-cart-view', args=('satchless_cart',)))

    def test_prepare_order_redirects_to_checkout_when_order_exists(self):
        order = self._create_order(self.anon_client)
        response = self._test_status(reverse(prepare_order), method='post',
                                     client_instance=self.anon_client, status_code=302)
        self.assertRedirects(response, reverse(views.checkout,
                                               kwargs={'order_token':
                                                       order.token}))

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

    def test_order_is_deleted_when_all_cart_items_are_deleted(self):
        order = self._create_order(self.anon_client)
        for cart_item in order.cart.items.all():
            self.assertTrue(Order.objects.filter(pk=order.pk).exists())
            order.cart.set_quantity(cart_item.variant, 0)
        self.assertFalse(Order.objects.filter(pk=order.pk).exists())

    def test_checkout_view(self):
        order = self._create_order(self.anon_client)
        response = self._test_status(reverse(views.checkout,
                                             kwargs={'order_token':
                                                     order.token}),
                                     client_instance=self.anon_client,
                                     status_code=200)
        group = order.groups.get()
        dtypes = order_handler.get_delivery_types(group)
        dtype = dtypes[0][0]
        df = response.context['delivery_formset']
        data = {'billing_first_name': 'First',
                'billing_last_name': 'Last',
                'billing_street_address_1': 'Via Rodeo 1',
                'billing_city': 'Beverly Hills',
                'billing_country': 'US',
                'billing_country_area': 'AZ',
                'billing_phone': '555-555-5555',
                'billing_postal_code': '90210'}
        data[df.add_prefix('INITIAL_FORMS')] = '1'
        data[df.add_prefix('MAX_NUM_FORMS')] = ''
        data[df.add_prefix('TOTAL_FORMS')] = '1'
        for form in df.forms:
            data[form.add_prefix('delivery_type')] = dtype
            data[form.add_prefix('id')] = group.id
        self._test_status(reverse(views.checkout, kwargs={'order_token':
                                                          order.token}),
                          data=data, status_code=302,
                          client_instance=self.anon_client, method='post')
        self.assertEqual(order.groups.get().delivery_type, dtype)

    def test_delivery_details_view(self):
        order = self._create_order(self.anon_client)
        group = order.groups.get()
        dtypes = order_handler.get_delivery_types(group)
        group.delivery_type = dtypes[0][0]
        group.save()
        self._test_status(reverse(views.delivery_details,
                                  kwargs={'order_token': order.token}),
                          client_instance=self.anon_client, method='get')

    def test_delivery_details_view_redirects_to_checkout_when_delivery_type_is_missing(self):
        order = self._create_order(self.anon_client)
        response = self._test_status(reverse(views.delivery_details,
                                             kwargs={'order_token':
                                                     order.token}),
                                     status_code=302,
                                     client_instance=self.anon_client,
                                     method='get')
        self.assertRedirects(response, reverse(views.checkout,
                                               kwargs={'order_token':
                                                       order.token}))

    def test_payment_view_redirects_to_payment_choice_view_when_payment_type_is_missing(self):
        order = self._create_order(self.anon_client)
        response = self._test_status(reverse(views.payment_details,
                                             kwargs={'order_token':
                                                     order.token}),
                                     status_code=302,
                                     client_instance=self.anon_client,
                                     method='get')
        self.assertRedirects(response, reverse(views.payment_choice,
                                               kwargs={'order_token':
                                                       order.token}))

    def test_checkout_views_redirects_to_confirmation_page_when_order_has_payment_pending_status(self):
        order = self._create_order(self.anon_client)
        order.set_status('payment-pending')

        self._test_status(reverse(views.payment_details,
                                  kwargs={'order_token':
                                          order.token}),
                                  status_code=302,
                                  client_instance=self.anon_client,
                                  method='get')

    def test_reactive_order_view_changes_order_status_to_checkout(self):
        order = self._create_order(self.anon_client)
        order.set_status('payment-failed')

        self._test_status(reverse(reactivate_order,
                                  kwargs={'order_token':
                                          order.token}),
                                  status_code=302,
                                  client_instance=self.anon_client,
                                  method='post')
        self.assertEqual(Order.objects.get(pk=order.pk).status, 'checkout')

    def test_reactive_order_view_redirects_to_checkout_for_correct_order(self):
        order = self._create_order(self.anon_client)
        order.set_status('payment-failed')

        response = self._test_status(reverse(reactivate_order,
                                     kwargs={'order_token':
                                             order.token}),
                                     status_code=302,
                                     client_instance=self.anon_client,
                                     method='post')
        self.assertRedirects(response, reverse('satchless-checkout', args=(order.token,)))

    def test_require_order_decorator(self):
        def assertRedirects(response, path):
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response['Location'], path)

        def view_factory(status):
            @require_order(status=status)
            def view(request, order_token):
                return HttpResponse()
            return view
        request = HttpRequest()
        order = self._create_order(self.anon_client)

        # decorator should not redirect if status is correct
        for status, name in Order.STATUS_CHOICES:
            view = view_factory(status)
            order.set_status(status)
            self.assertTrue(view(request, order_token=order.token).status_code, 200)


        view = view_factory('non-existing-status')

        order.set_status('payment-pending')
        assertRedirects(view(request, order_token=order.token),
                        reverse('satchless-checkout-confirmation', args=(order.token,)))

        order.set_status('checkout')
        assertRedirects(view(request, order_token=order.token),
                        reverse('satchless-checkout', args=(order.token,)))

        for status in ('payment-failed', 'delivery', 'payment-complete', 'cancelled'):
            order.set_status(status)
            assertRedirects(view(request, order_token=order.token),
                            reverse('satchless-order-view', args=(order.token,)))

        assertRedirects(view(request, order_token='non-existing-order-token'),
                        reverse('satchless-cart-view'))
