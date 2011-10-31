# -*- coding: utf-8 -*-
import os

from decimal import Decimal
from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import Client

from .....checkout.tests import BaseCheckoutAppTests
from .....contrib.delivery.simplepost.models import PostShippingType
from .....order import handler as order_handler
from .....payment import ConfirmationFormNeeded
from .....payment.tests import TestPaymentProvider
from .....pricing import handler as pricing_handler
from .....product.tests import DeadParrot
from .....product.tests.pricing import FiveZlotyPriceHandler


from .. import app
from .....cart.tests import TestCart
from .....order.tests import TestOrder

class TestPaymentProviderWithConfirmation(TestPaymentProvider):
    def confirm(self, order, typ=None):
        raise ConfirmationFormNeeded(action='http://test.payment.gateway.example.com')


class CheckoutTest(BaseCheckoutAppTests):
    checkout_app = app.checkout_app
    urls = BaseCheckoutAppTests.MockUrls(checkout_app=app.checkout_app)

    def setUp(self):
        self.checkout_app.cart_model = TestCart
        self.checkout_app.order_model = TestOrder
        self.macaw = DeadParrot.objects.create(slug='macaw',
                species="Hyacinth Macaw")
        self.cockatoo = DeadParrot.objects.create(slug='cockatoo',
                species="White Cockatoo")
        self.macaw_blue = self.macaw.variants.create(color='blue',
                                                     looks_alive=False)
        self.macaw_blue_fake = self.macaw.variants.create(color='blue',
                                                          looks_alive=True)
        self.cockatoo_white_a = self.cockatoo.variants.create(color='white',
                                                              looks_alive=True)
        self.cockatoo_white_d = self.cockatoo.variants.create(color='white',
                                                              looks_alive=False)
        self.cockatoo_blue_a = self.cockatoo.variants.create(color='blue',
                                                             looks_alive=True)
        self.cockatoo_blue_d = self.cockatoo.variants.create(color='blue',
                                                             looks_alive=False)

        test_dir = os.path.dirname(__file__)
        satchless_dir = os.path.join(test_dir, '..', '..', '..', '..')
        self.custom_settings = {
            'SATCHLESS_DJANGO_PAYMENT_TYPES': ['dummy'],
            'PAYMENT_VARIANTS': {'dummy': ('payments.dummy.DummyProvider', {'url': '/', })},
            'TEMPLATE_DIRS': (os.path.join(satchless_dir, 'category', 'templates'),
                              os.path.join(satchless_dir, 'order', 'templates'),
                              os.path.join(test_dir, '..', 'templates'),
                              os.path.join(test_dir, 'templates')),
            'TEMPLATE_LOADERS': (
                'django.template.loaders.filesystem.Loader',
            )
        }
        self.original_settings = self._setup_settings(self.custom_settings)
        order_handler.delivery_queue = order_handler.DeliveryQueue('satchless.contrib.delivery.simplepost.PostDeliveryProvider')
        order_handler.payment_queue = order_handler.PaymentQueue(TestPaymentProviderWithConfirmation)
        order_handler.partitioner_queue = order_handler.PartitionerQueue('satchless.contrib.order.partitioner.simple.SimplePartitioner')

        self.anon_client = Client()

        PostShippingType.objects.create(price=12, typ='polecony', name='list polecony')
        PostShippingType.objects.create(price=20, typ='list', name='List zwykly')

        self.original_handlers = settings.SATCHLESS_PRICING_HANDLERS
        pricing_handler.pricing_queue = pricing_handler.PricingQueue(FiveZlotyPriceHandler)

    def tearDown(self):
        self._teardown_settings(self.original_settings, self.custom_settings)
        pricing_handler.pricing_queue = pricing_handler.PricingQueue(*self.original_handlers)

    def test_order_from_cart_view_creates_proper_order(self):
        cart = self._get_or_create_cart_for_client(self.anon_client)
        cart.replace_item(self.macaw_blue, 1)
        cart.replace_item(self.macaw_blue_fake, Decimal('2.45'))
        cart.replace_item(self.cockatoo_white_a, Decimal('2.45'))

        self._test_status(self.checkout_app.reverse('prepare-order'),
                          method='post', client_instance=self.anon_client,
                          status_code=302)

        order = self._get_order_from_session(self.anon_client.session)
        self.assertNotEqual(order, None)
        order_items = self._get_order_items(order)
        self.assertEqual(set(cart.items.values_list('variant', 'quantity')),
                         order_items)

    def test_order_is_updated_after_cart_changes(self):
        cart = self._get_or_create_cart_for_client(self.anon_client)

        cart.replace_item(self.macaw_blue, 1)
        cart.replace_item(self.macaw_blue_fake, Decimal('2.45'))
        cart.replace_item(self.cockatoo_white_a, Decimal('2.45'))

        self._test_status(self.checkout_app.reverse('prepare-order'),
                          method='post', client_instance=self.anon_client,
                          status_code=302)

        order = self._get_order_from_session(self.anon_client.session)
        order_items = self._get_order_items(order)
        # compare cart and order
        self.assertEqual(set(cart.items.values_list('variant', 'quantity')),
                         order_items)

        # update cart
        cart.add_item(self.macaw_blue, 100)
        cart.add_item(self.macaw_blue_fake, 100)
        self._test_status(self.checkout_app.reverse('prepare-order'),
                          method='post', client_instance=self.anon_client,
                          status_code=302)

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
        cart.replace_item(self.macaw_blue, 1)
        response = self._test_status(self.checkout_app.reverse('prepare-order'),
                                     method='post',
                                     client_instance=self.anon_client,
                                     status_code=302)
        order_pk = self.anon_client.session.get('satchless_order', None)
        order = self.checkout_app.order_model.objects.get(pk=order_pk)
        self.assertRedirects(response, self.checkout_app.reverse('checkout',
                                                                 kwargs={'order_token':
                                                                         order.token}))

    def test_prepare_order_redirects_to_cart_when_cart_is_empty(self):
        self._get_or_create_cart_for_client(self.anon_client)
        response = self._test_status(self.checkout_app.reverse('prepare-order'),
                                     method='post',
                                     client_instance=self.anon_client,
                                     status_code=302)
        self.assertRedirects(response, reverse('cart:details'))

    def test_prepare_order_redirects_to_checkout_when_order_exists(self):
        order = self._create_order(self.anon_client)
        response = self._test_status(self.checkout_app.reverse('prepare-order'),
                                     method='post',
                                     client_instance=self.anon_client,
                                     status_code=302)
        self.assertRedirects(response, self.checkout_app.reverse('checkout',
                                                                 kwargs={'order_token':
                                                                         order.token}))

    def test_order_is_deleted_when_all_cart_items_are_deleted(self):
        order = self._create_order(self.anon_client)
        for cart_item in order.cart.get_all_items():
            self.assertTrue(self.checkout_app.order_model.objects.filter(pk=order.pk).exists())
            order.cart.replace_item(cart_item.variant, 0)
        self.assertFalse(self.checkout_app.order_model.objects.filter(pk=order.pk).exists())

    def test_checkout_view(self):
        order = self._create_order(self.anon_client)
        response = self._test_status(self.checkout_app.reverse('checkout',
                                                               kwargs={'order_token':
                                                                       order.token}),
                                     client_instance=self.anon_client,
                                     status_code=200)
        group = order.groups.get()
        dtypes = list(order_handler.delivery_queue.enum_types(group))
        dtype = dtypes[0][1].typ
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
        response = self._test_status(self.checkout_app.reverse('checkout',
                                                               kwargs={'order_token':
                                                                       order.token}),
                                     data=data, status_code=302,
                                     client_instance=self.anon_client, method='post')
        self.assertEqual(order.groups.get().delivery_type, dtype)
        self.assertRedirects(response, self.checkout_app.reverse('delivery-details',
                                                                 kwargs={'order_token':
                                                                         order.token}))

    def test_delivery_details_view(self):
        order = self._create_order(self.anon_client)
        group = order.groups.get()
        dtypes = list(order_handler.delivery_queue.enum_types(group))
        group.delivery_type = dtypes[0][1].typ
        group.save()
        response = self._test_status(self.checkout_app.reverse('delivery-details',
                                                               kwargs={'order_token':
                                                                       order.token}),
                                     client_instance=self.anon_client, method='get')
        group, delivery_type, form = response.context['delivery_group_forms'][0]

        data = {
                u'shipping_first_name': u'First',
                u'shipping_last_name': u'Last',
                u'shipping_company_name': u'TV Company',
                u'shipping_street_address_1': u'Woronicza',
                u'shipping_street_address_2': u'',
                u'shipping_postal_code': u'66-620',
                u'shipping_city': u'Warszawa',
                u'shipping_country_area': u'Mazowieckie',
                u'shipping_phone': u'022 000 888',
                u'shipping_country': u'PL'}

        data = dict((form.add_prefix(key), data[key]) for key in data)
        response = self._test_POST_status(self.checkout_app.reverse('delivery-details',
                                                                    kwargs={'order_token':
                                                                            order.token}),
                                          data=data, client_instance=self.anon_client)
        self.assertRedirects(response, self.checkout_app.reverse('payment-choice',
                                                                 kwargs={'order_token':
                                                                         order.token}))

    def test_payment_choice_view(self):
        order = self._create_order(self.anon_client)
        group = order.groups.get()
        dtypes = list(order_handler.delivery_queue.enum_types(group))
        group.delivery_type = dtypes[0][1].typ
        group.save()

        pprovider, ptype = list(order_handler.payment_queue.enum_types(group))[0]
        self._test_GET_status(self.checkout_app.reverse('payment-choice',
                                                        kwargs={'order_token':
                                                                order.token}),
                              client_instance=self.anon_client)
        data = {
            'payment_type': ptype.typ
        }
        response = self._test_POST_status(self.checkout_app.reverse('payment-choice',
                                                                    kwargs={'order_token':
                                                                            order.token}),
                                                  data=data,
                                          client_instance=self.anon_client)
        # TestPaymentProvider doesn't provide any additional form so
        # payment details view redirects to confirmation page
        self.assertRedirects(response, self.checkout_app.reverse('payment-details',
                                                                 kwargs={'order_token':
                                                                         order.token}),
                             target_status_code=302)

    def test_delivery_details_view_redirects_to_checkout_when_delivery_type_is_missing(self):
        order = self._create_order(self.anon_client)
        response = self._test_status(self.checkout_app.reverse('delivery-details',
                                                               kwargs={'order_token':
                                                                       order.token}),
                                     status_code=302,
                                     client_instance=self.anon_client,
                                     method='get')
        self.assertRedirects(response, self.checkout_app.reverse('checkout',
                                                                 kwargs={'order_token':
                                                                         order.token}))

    def test_payment_view_redirects_to_payment_choice_view_when_payment_type_is_missing(self):
        order = self._create_order(self.anon_client)
        response = self._test_status(self.checkout_app.reverse('payment-details',
                                                               kwargs={'order_token':
                                                                       order.token}),
                                     status_code=302,
                                     client_instance=self.anon_client,
                                     method='get')
        self.assertRedirects(response, self.checkout_app.reverse('payment-choice',
                                                                 kwargs={'order_token':
                                                                         order.token}))

    def test_checkout_views_redirects_to_confirmation_page_when_order_has_payment_pending_status(self):
        order = self._create_order(self.anon_client)
        order.set_status('payment-pending')

        self._test_status(self.checkout_app.reverse('payment-details',
                                                    kwargs={'order_token':
                                                            order.token}),
                                  status_code=302,
                                  client_instance=self.anon_client,
                                  method='get')

    def test_reactive_order_view_changes_order_status_to_checkout(self):
        order = self._create_order(self.anon_client)
        order.set_status('payment-failed')

        self._test_status(self.checkout_app.reverse('reactivate-order',
                                                    kwargs={'order_token':
                                                            order.token}),
                                  status_code=302,
                                  client_instance=self.anon_client,
                                  method='post')
        self.assertEqual(self.checkout_app.order_model.objects.get(pk=order.pk).status, 'checkout')

