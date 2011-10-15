# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.test import Client

from ...cart import urls as cart_urls
from ...cart.models import CART_SESSION_KEY
from ...order.app import order_app
from ...pricing import handler as pricing_handler
from ...product.tests import DeadParrot
from ...product.tests.pricing import FiveZlotyPriceHandler
from ...util.tests import ViewsTestCase

from ..app import CheckoutApp

class BaseCheckoutAppTests(ViewsTestCase):
    class MockUrls:
        def __init__(self, checkout_app):
            self.urlpatterns = patterns('',
                url(r'^cart/', include(cart_urls)),
                url(r'^checkout/', include(checkout_app.get_urls())),
                url(r'^order/', include(order_app.get_urls())),
            )

    def _create_cart(self, client):
        cart = self._get_or_create_cart_for_client(client)
        cart.set_quantity(self.macaw_blue, 1)
        return cart

    def _get_or_create_cart_for_client(self, client, typ='satchless_cart'):
        self._test_status(reverse('satchless-cart-view'),
                          client_instance=client)
        return self.checkout_app.cart_model.objects.get(pk=client.session[CART_SESSION_KEY % typ],
                                                        typ=typ)

    def _get_or_create_order_for_client(self, client):
        self._test_status(reverse(self.checkout_app.prepare_order), method='post',
                          client_instance=client, status_code=302)
        order_pk = client.session.get('satchless_order', None)
        return self.checkout_app.order_model.objects.get(pk=order_pk)

    def _create_order(self, client):
        self._create_cart(client)
        self._test_status(reverse(self.checkout_app.prepare_order), method='post',
                          client_instance=client, status_code=302)
        return self._get_order_from_session(client.session)

    def _get_order_from_session(self, session):
        order_pk = session.get('satchless_order', None)
        if order_pk:
            return self.checkout_app.order_model.objects.get(pk=order_pk)
        return None

    def _get_order_items(self, order):
        order_items = set()
        for group in order.groups.all():
            order_items.update(group.items.values_list('product_variant',
                                                       'quantity'))
        return order_items


class MockCheckoutApp(CheckoutApp):
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
        pricing_handler.pricing_queue = pricing_handler.PricingQueue(FiveZlotyPriceHandler)

    def tearDown(self):
        #self._teardown_settings(self.original_settings, self.custom_settings)
        pricing_handler.pricing_queue = pricing_handler.PricingQueue(*self.original_handlers)


    def test_reactive_order_view_redirects_to_checkout_for_correct_order(self):
        order = self._create_order(self.anon_client)
        order.set_status('payment-failed')

        response = self._test_status(reverse(self.checkout_app.reactivate_order,
                                     kwargs={'order_token':
                                             order.token}),
                                     status_code=302,
                                     client_instance=self.anon_client,
                                     method='post')
        self.assertRedirects(response, reverse(self.checkout_app.checkout,
                                               args=(order.token,)))

    def test_redirect_order(self):
        def assertRedirects(response, path):
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response['Location'], path)
        order = self._create_order(self.anon_client)

        order.set_status('payment-pending')
        assertRedirects(self.checkout_app.redirect_order(order),
                        reverse(self.checkout_app.confirmation, args=(order.token,)))

        order.set_status('checkout')
        assertRedirects(self.checkout_app.redirect_order(order),
                        reverse(self.checkout_app.checkout, args=(order.token,)))

        for status in ('payment-failed', 'delivery', 'payment-complete', 'cancelled'):
            order.set_status(status)
            response = self.checkout_app.redirect_order(order)
            assertRedirects(response,
                            reverse('satchless-order-view', args=(order.token,)))

        assertRedirects(self.checkout_app.redirect_order(None),
                        self.checkout_app.get_no_order_redirect_url())

