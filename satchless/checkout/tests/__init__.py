# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.test import Client

from ..app import CheckoutApp
from ...cart.tests import cart_app
from ...core.app import view
from ...order.tests import order_app
from ...pricing import handler as pricing_handler
from ...product.tests import DeadParrot
from ...product.tests.pricing import FiveZlotyPriceHandler
from ...util.tests import ViewsTestCase


class BaseCheckoutAppTests(ViewsTestCase):
    class MockUrls:
        def __init__(self, checkout_app):
            self.urlpatterns = patterns('',
                url(r'^cart/', include(cart_app.urls)),
                url(r'^checkout/', include(checkout_app.urls)),
                url(r'^order/', include(order_app.urls)),
            )

    def _create_cart(self, client):
        cart = self._get_or_create_cart_for_client(client)
        cart.replace_item(self.macaw_blue, 1)
        return cart

    def _get_or_create_cart_for_client(self, client):
        self._test_status(cart_app.reverse('details'),
                          client_instance=client)
        token = client.session[cart_app.cart_session_key]
        return self.checkout_app.Cart.objects.get(token=token, typ=cart_app.cart_type)

    def _get_or_create_order_for_client(self, client):
        cart = self._get_or_create_cart_for_client(client)
        self._test_status(
            self.checkout_app.reverse('prepare-order',
                                      kwargs={'cart_token': cart.token}),
            method='post', client_instance=client, status_code=302)
        order_pk = client.session.get('satchless_order', None)
        return self.checkout_app.Order.objects.get(pk=order_pk)

    def _create_order(self, client):
        cart = self._create_cart(client)
        self._test_status(
            self.checkout_app.reverse('prepare-order',
                                      kwargs={'cart_token': cart.token}),
            method='post', client_instance=client, status_code=302)
        return self._get_order_from_session(client.session)

    def _get_order_from_session(self, session):
        order_pk = session.get('satchless_order', None)
        if order_pk:
            return self.checkout_app.Order.objects.get(pk=order_pk)
        return None

    def _get_order_items(self, order):
        order_items = set()
        for group in order.groups.all():
            order_items.update(group.items.values_list('product_variant',
                                                       'quantity'))
        return order_items


class MockCheckoutApp(CheckoutApp):

    cart_type = cart_app.cart_type
    Cart = cart_app.Cart
    Order = order_app.Order

    @view(r'^(?P<order_token>\w+)/$', name='checkout')
    def checkout(self, *args, **kwargs):
        return HttpResponse()


class App(BaseCheckoutAppTests):
    checkout_app = MockCheckoutApp()
    urls = BaseCheckoutAppTests.MockUrls(checkout_app)

    def setUp(self):
        self.anon_client = Client()
        self.macaw = DeadParrot.objects.create(slug='macaw',
                                               species="Hyacinth Macaw")
        self.macaw_blue = self.macaw.variants.create(color='blue',
                                                     looks_alive=False)
        self.original_handlers = settings.SATCHLESS_PRICING_HANDLERS
        pricing_handler.pricing_queue = pricing_handler.PricingQueue(
            FiveZlotyPriceHandler)

    def tearDown(self):
        #self._teardown_settings(self.original_settings, self.custom_settings)
        pricing_handler.pricing_queue = pricing_handler.PricingQueue(
            *self.original_handlers)

    def test_reactive_order_view_redirects_to_checkout_for_correct_order(self):
        order = self._create_order(self.anon_client)
        order.set_status('payment-failed')

        response = self._test_status(
            self.checkout_app.reverse('reactivate-order',
                                      kwargs={'order_token': order.token}),
            status_code=302, client_instance=self.anon_client, method='post')
        self.assertRedirects(response,
                             self.checkout_app.reverse('checkout',
                                                       args=(order.token,)))

    def test_redirect_order(self):
        def assertRedirects(response, path):
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response['Location'], path)
        order = self._create_order(self.anon_client)

        order.set_status('payment-pending')
        assertRedirects(self.checkout_app.redirect_order(order),
                        self.checkout_app.reverse('confirmation',
                                                  args=(order.token,)))

        order.set_status('checkout')
        assertRedirects(self.checkout_app.redirect_order(order),
                        self.checkout_app.reverse('checkout',
                                                  args=(order.token,)))

        for status in ('payment-failed', 'delivery', 'payment-complete',
                       'cancelled'):
            order.set_status(status)
            response = self.checkout_app.redirect_order(order)
            assertRedirects(response,
                            reverse('order:details', args=(order.token,)))

        assertRedirects(self.checkout_app.redirect_order(None),
                        reverse('cart:details'))