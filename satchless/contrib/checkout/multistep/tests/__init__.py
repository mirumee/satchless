# -*- coding: utf-8 -*-
import os

from decimal import Decimal
from django.core.urlresolvers import reverse
from django.forms.models import modelform_factory
from django import forms
from django.test import Client

from .....checkout.tests import BaseCheckoutAppTests
from .....contrib.delivery.simplepost.models import PostShippingType
from .....contrib.order.partitioner.simple import SimplePhysicalPartitioner
from .....order import handler as order_handler
from .....order import forms as order_forms
from .....payment import ConfirmationFormNeeded
from .....payment.tests import TestPaymentProvider
from .....product.tests import DeadParrot

from .. import app
from .....cart.tests import cart_app
from .....delivery.tests import TestDeliveryProvider, TestDeliveryType
from .....order.tests import order_app


class TestPaymentProviderWithConfirmation(TestPaymentProvider):
    def confirm(self, order, typ=None):
        raise ConfirmationFormNeeded(
            action='http://test.payment.gateway.example.com')


class PaymentConfigurationForm(forms.Form):
    customer_id = forms.CharField(max_length=64)


class TestPaymentProviderWithForm(TestPaymentProvider):
    def get_configuration_form(self, order, data, typ=None):
        return PaymentConfigurationForm(data=data)


class TestCheckoutApp(app.MultiStepCheckoutApp):
    Order = order_app.Order

    BillingForm = modelform_factory(order_app.Order,
                                    order_forms.BillingForm)
    ShippingForm = modelform_factory(
        order_app.DeliveryGroup,
        form=order_forms.ShippingForm,
        fields=order_forms.ShippingForm._meta.fields)
    DeliveryMethodForm = modelform_factory(
        order_app.DeliveryGroup,
        form=order_forms.DeliveryMethodForm,
        fields=order_forms.DeliveryMethodForm._meta.fields)


class CheckoutTestCase(BaseCheckoutAppTests):
    checkout_app = TestCheckoutApp(
        cart_app=cart_app,
        delivery_provider=TestDeliveryProvider(),
        payment_provider=TestPaymentProviderWithConfirmation(),
        delivery_partitioner=SimplePhysicalPartitioner())
    urls = BaseCheckoutAppTests.MockUrls(checkout_app=checkout_app)

    def setUp(self):
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
            'PAYMENT_VARIANTS': {'dummy': ('payments.dummy.DummyProvider',
                                           {'url': '/', })},
            'TEMPLATE_DIRS': (os.path.join(satchless_dir, 'cart', 'templates'),
                              os.path.join(satchless_dir, 'category', 'templates'),
                              os.path.join(satchless_dir, 'order', 'templates'),
                              os.path.join(test_dir, '..', 'templates'),
                              os.path.join(test_dir, 'templates')),
            'TEMPLATE_LOADERS': (
                'django.template.loaders.filesystem.Loader',
            )
        }
        TestDeliveryType.objects.create(price=10, typ='pidgin', name='Pidgin')
        TestDeliveryType.objects.create(price=15, typ='courier', name='Courier',
                                        with_customer_notes=True)

        self.original_settings = self._setup_settings(self.custom_settings)
        self.anon_client = Client()

        PostShippingType.objects.create(price=12, typ='polecony',
                                        name='list polecony')
        PostShippingType.objects.create(price=20, typ='list',
                                        name='List zwykly')

    def tearDown(self):
        self._teardown_settings(self.original_settings, self.custom_settings)

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

    def test_partitioned_correctly_after_cart_changes(self):
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

        # repartition
        self._test_status(self.checkout_app.reverse('prepare-order'),
                          method='post', client_instance=self.anon_client,
                          status_code=302)
        order = self._get_order_from_session(self.anon_client.session)
        order_items = self._get_order_items(order)
        # compare cart and order
        self.assertEqual(set(cart.items.values_list('variant', 'quantity')),
                         order_items)

    def test_prepare_order_creates_order_and_redirects_to_checkout_when_cart_is_not_empty(self):
        cart = self._get_or_create_cart_for_client(self.anon_client)
        cart.replace_item(self.macaw_blue, 1)
        response = self._test_status(
            self.checkout_app.reverse('prepare-order'),
            method='post', client_instance=self.anon_client, status_code=302)
        order_pk = self.anon_client.session.get(self.checkout_app.order_session_key, None)
        order = self.checkout_app.Order.objects.get(pk=order_pk)
        self.assertRedirects(response,
                             self.checkout_app.reverse('checkout',
                                                       kwargs={'order_token':
                                                               order.token}))

    def test_prepare_order_redirects_to_cart_when_cart_is_empty(self):
        self._get_or_create_cart_for_client(self.anon_client)
        response = self._test_status(
            self.checkout_app.reverse('prepare-order'),
            method='post', client_instance=self.anon_client, status_code=302)
        self.assertRedirects(response, reverse('cart:details'))

    def test_prepare_order_redirects_to_checkout_when_order_exists_and_is_not_empty(self):
        self._get_or_create_cart_for_client(self.anon_client)
        order = self._create_order(self.anon_client)
        response = self._test_status(
            self.checkout_app.reverse('prepare-order'),
            method='post', client_instance=self.anon_client, status_code=302)
        self.assertRedirects(response,
                             self.checkout_app.reverse('checkout',
                                                       kwargs={'order_token':
                                                               order.token}))

    def test_delivery_method_view(self):
        order = self._create_order(self.anon_client)
        group = order.groups.get()
        self.assertTrue(group.require_shipping_address)
        dtypes = list(self.checkout_app.delivery_queue.enum_types(group))
        dtype = dtypes[0].typ
        response = self._test_status(
            self.checkout_app.reverse('delivery-method',
                                      kwargs={'order_token': order.token}),
            client_instance=self.anon_client, status_code=200)
        data = {}
        df = response.context['delivery_method_formset']
        data[df.add_prefix('INITIAL_FORMS')] = len(df.forms)
        data[df.add_prefix('MAX_NUM_FORMS')] = ''
        data[df.add_prefix('TOTAL_FORMS')] = len(df.forms)
        for form in df.forms:
            data[form.add_prefix('delivery_type')] = dtype
            data[form.add_prefix('id')] = group.id
        response = self._test_status(
            self.checkout_app.reverse('delivery-method',
                                      kwargs={'order_token': order.token}),
            data=data, status_code=302, client_instance=self.anon_client,
            method='post')
        self.assertEqual(order.groups.get().delivery_type, dtype)
        self.assertRedirects(response,
                             self.checkout_app.reverse('delivery-details',
                                                       kwargs={'order_token':
                                                               order.token}),
                             target_status_code=302)

    def test_checkout_view(self):
        order = self._create_order(self.anon_client)
        group = order.groups.get()
        dtypes = list(self.checkout_app.delivery_queue.enum_types(group))
        group.delivery_type = dtypes[0].typ
        group.save()
        response = self._test_status(
            self.checkout_app.reverse('checkout',
                                      kwargs={'order_token': order.token}),
            client_instance=self.anon_client, method='get')
        data = {'billing_first_name': 'First',
                'billing_last_name': 'Last',
                'billing_street_address_1': 'Via Rodeo 1',
                'billing_city': 'Beverly Hills',
                'billing_country': 'US',
                'billing_country_area': 'AZ',
                'billing_phone': '555-555-5555',
                'billing_postal_code': '90210'}
        shipping_data = {
                'shipping_first_name': 'First',
                'shipping_last_name': 'Last',
                'shipping_company_name': 'TV Company',
                'shipping_street_address_1': 'Woronicza',
                'shipping_street_address_2': '',
                'shipping_postal_code': '66-620',
                'shipping_city': 'Warszawa',
                'shipping_country_area': 'Mazowieckie',
                'shipping_phone': '022 000 888',
                'shipping_country': 'PL'}
        df = response.context['shipping_formset']
        data[df.add_prefix('INITIAL_FORMS')] = len(df.forms)
        data[df.add_prefix('MAX_NUM_FORMS')] = ''
        data[df.add_prefix('TOTAL_FORMS')] = len(df.forms)
        for form in df.forms:
            form_data = dict((form.add_prefix(key), shipping_data[key])
                                 for key in shipping_data)
            form_data[form.add_prefix('id')] = group.id
            data.update(form_data)
        response = self._test_POST_status(
            self.checkout_app.reverse('checkout',
                                      kwargs={'order_token': order.token}),
            data=data, client_instance=self.anon_client)
        self.assertRedirects(response,
                             self.checkout_app.reverse('delivery-method',
                                                       kwargs={'order_token':
                                                               order.token}))

    def test_payment_choice_view(self):
        order = self._create_order(self.anon_client)
        group = order.groups.get()
        dtypes = list(self.checkout_app.delivery_queue.enum_types(group))
        group.delivery_type = dtypes[0].typ
        group.save()

        ptype = list(self.checkout_app.payment_queue.enum_types(group))[0]
        self._test_GET_status(self.checkout_app.reverse('payment-method',
                                                        kwargs={'order_token':
                                                                order.token}),
                              client_instance=self.anon_client)
        data = {
            'payment_type': ptype.typ
        }
        response = self._test_POST_status(
            self.checkout_app.reverse('payment-method',
                                      kwargs={'order_token': order.token}),
            data=data, client_instance=self.anon_client)
        # TestPaymentProvider doesn't provide any additional form so
        # payment details view redirects to confirmation page
        self.assertRedirects(response,
                             self.checkout_app.reverse('payment-details',
                                                       kwargs={'order_token':
                                                               order.token}),
                             target_status_code=302)

    def test_payment_details_view(self):
        order = self._create_order(self.anon_client)
        group = order.groups.get()
        dtypes = list(self.checkout_app.delivery_queue.enum_types(group))
        group.delivery_type = dtypes[0].typ
        group.save()

        ptype = list(self.checkout_app.payment_queue.enum_types(group))[0]
        order.payment_type = ptype.typ
        order.save()

        self.checkout_app.payment_queue = order_handler.PaymentQueue(
            TestPaymentProviderWithForm)

        self._test_status(self.checkout_app.reverse('payment-details',
                                                    kwargs={'order_token':
                                                            order.token}),
                          status_code=200, client_instance=self.anon_client,
                          method='get')

    def test_delivery_details_view_redirects_to_delivery_method_when_delivery_type_is_missing(self):
        order = self._create_order(self.anon_client)
        response = self._test_status(
            self.checkout_app.reverse('delivery-details',
                                      kwargs={'order_token': order.token}),
            status_code=302, client_instance=self.anon_client, method='get')
        self.assertRedirects(response,
                             self.checkout_app.reverse('delivery-method',
                                                       kwargs={'order_token':
                                                               order.token}))

    def test_delivery_details_view(self):
        order = self._create_order(self.anon_client)
        group = order.groups.get()
        # delivery type which requires customer info
        delivery_type = TestDeliveryType.objects.filter(with_customer_notes=True)[0]
        group.delivery_type = delivery_type.typ
        group.save()
        response = self._test_status(
            self.checkout_app.reverse('delivery-details',
                                      kwargs={'order_token': order.token}),
            status_code=200, client_instance=self.anon_client, method='get')
        df = response.context['delivery_group_forms']
        data = {}
        for group, typ, form in df:
            data[form.add_prefix('notes')] = ('Intercom is broken - '
                                              'pleas call me on my mobile phone')
        response = self._test_POST_status(
            self.checkout_app.reverse('delivery-details',
                                      kwargs={'order_token': order.token}),
            data=data, client_instance=self.anon_client)
        self.assertRedirects(response,
                             self.checkout_app.reverse('payment-method',
                                                       kwargs={'order_token':
                                                               order.token}))

    def test_delivery_details_view_without_form(self):
        order = self._create_order(self.anon_client)
        group = order.groups.get()
        # delivery type which should be constructed without additional details
        delivery_type = TestDeliveryType.objects.filter(with_customer_notes=False)[0]
        group.delivery_type = delivery_type.typ
        group.save()
        response = self._test_status(
            self.checkout_app.reverse('delivery-details',
                                      kwargs={'order_token': order.token}),
            status_code=302, client_instance=self.anon_client, method='get')
        self.assertRedirects(response,
                             self.checkout_app.reverse('payment-method',
                                                       kwargs={'order_token':
                                                               order.token}))

    def test_payment_view_redirects_to_payment_choice_view_when_payment_type_is_missing(self):
        order = self._create_order(self.anon_client)
        response = self._test_status(
            self.checkout_app.reverse('payment-details',
                                      kwargs={'order_token': order.token}),
            status_code=302, client_instance=self.anon_client, method='get')
        self.assertRedirects(response,
                             self.checkout_app.reverse('payment-method',
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
        self.assertEqual(
            self.checkout_app.Order.objects.get(pk=order.pk).status,
            'checkout')
