# -*- coding: utf-8 -*-
import os

from django.conf.urls.defaults import patterns, include, url
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.test import Client

from ..app import CheckoutApp
from ...cart.tests import cart_app
from ...core.app import view
from ...order.tests import order_app
from ...product.tests import DeadParrot
from ...util.tests import ViewsTestCase


class BaseCheckoutAppTests(ViewsTestCase):
    class MockUrls:
        def __init__(self, checkout_app):
            self.urlpatterns = patterns('',
                url(r'^cart/', include(cart_app.urls)),
                url(r'^checkout/', include(checkout_app.urls)),
                url(r'^order/', include(order_app.urls)),
            )

    def setUp(self):
        test_dir = os.path.dirname(__file__)
        self.custom_settings = {
            'TEMPLATE_DIRS': [os.path.join(test_dir, 'templates'),
                              os.path.join(test_dir, '..', '..', 'cart', 'tests', 'templates')]
        }
        self.original_settings = self._setup_settings(self.custom_settings)

    def tearDown(self):
        self._teardown_settings(self.original_settings,
                                self.custom_settings)

    def _create_cart(self, client):
        cart = self._get_or_create_cart_for_client(client)
        cart.replace_item(self.macaw_blue, 1)
        return cart

    def _get_or_create_cart_for_client(self, client):
        self._test_status(cart_app.reverse('details'),
                          client_instance=client)
        token = client.session[cart_app.cart_session_key]
        return self.checkout_app.cart_app.Cart.objects.get(token=token)

    def _get_or_create_order_for_client(self, client):
        self._get_or_create_cart_for_client(client)
        self._test_status(
            self.checkout_app.reverse('prepare-order'),
            method='post', client_instance=client, status_code=302)
        order_pk = client.session.get(self.checkout_app.order_session_key, None)
        return self.checkout_app.Order.objects.get(pk=order_pk)

    def _create_order(self, client):
        self._create_cart(client)
        self._test_status(
            self.checkout_app.reverse('prepare-order'),
            method='post', client_instance=client, status_code=302)
        return self._get_order_from_session(client.session)

    def _get_order_from_session(self, session):
        order_pk = session.get(self.checkout_app.order_session_key, None)
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

    Order = order_app.Order

    @view(r'^(?P<order_token>\w+)/$', name='checkout')
    def checkout(self, *args, **kwargs):
        return HttpResponse()


class AppTestCase(BaseCheckoutAppTests):
    checkout_app = MockCheckoutApp(cart_app=cart_app)
    urls = BaseCheckoutAppTests.MockUrls(checkout_app)

    def setUp(self):
        super(AppTestCase, self).setUp()
        self.anon_client = Client()
        self.macaw = DeadParrot.objects.create(slug='macaw',
                                               species="Hyacinth Macaw")
        self.macaw_blue = self.macaw.variants.create(color='blue',
                                                     looks_alive=False)

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
