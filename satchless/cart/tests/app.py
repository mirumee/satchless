# -*- coding: utf-8 -*-
import os

from decimal import Decimal
from django.conf.urls.defaults import patterns, include, url
from django.core.exceptions import ObjectDoesNotExist
import django.forms
from django.http import HttpResponse

from .. import app
from .. import forms
from ...checkout.app import CheckoutApp
from ...pricing import handler as pricing_handler, Price
from ...product.app import ProductApp
from ...product.tests.pricing import FiveZlotyPriceHandler
from ...util.tests import ViewsTestCase

class MockProduct(object):

    instances = {}

    def __init__(self, slug):
        if (self.pk, slug) in self.instances:
            raise ValueError('Product with given slug already exists')
        self.instances[(self.pk, slug)] = self

    @property
    def pk(self):
        return id(self)

    def get_subtype_instance(self):
        return self


class MockVariant(object):

    def __init__(self, product):
        self.product = product


class MockCart(object):

    instances = {}
    currency = 'PLN'

    def __init__(self, items=None):
        self._items = list(items) if items else []
        self.instances[self.token] = self

    @property
    def token(self):
        return id(self)

    def get_all_items(self):
        return self._items

    def replace_item(self, variant, quantity):
        try:
            item = dict((i.variant, i) for i in self._items)[variant]
        except KeyError:
            self._items.append(MockCartItem(self, variant,
                                            quantity=quantity))
        else:
            item.quantity = quantity
            if item.quantity <= 0:
                self._items.remove(item)

    def add_item(self, variant, quantity):
        try:
            item = dict((i.variant, i) for i in self._items)[variant]
        except KeyError:
            self._items.append(MockCartItem(self, variant,
                                            quantity=quantity))
        else:
            item.quantity += quantity
            if item.quantity <= 0:
                self._items.remove(item)

    def get_item(self, pk, **kwargs):
        try:
            return dict((i.id, i) for i in self._items)[int(pk)]
        except KeyError:
            raise ObjectDoesNotExist()


class MockCartItem(object):

    def __init__(self, cart, variant, quantity):
        self.cart = cart
        self.quantity = quantity
        self.variant = variant

    @property
    def id(self):
        return id(self)

    def get_unit_price(self, currency=None):
        return Price(10, currency=currency)

    def get_price(self, currency=None):
        return self.get_unit_price(currency=currency) * self.quantity


class MockOrder(object):
    pass


class TestProductApp(ProductApp):

    Product = MockProduct
    Variant = MockVariant


class CartItemForm(django.forms.Form, forms.QuantityForm):
    quantity = django.forms.DecimalField('Quantity', initial=1)

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance')
        super(CartItemForm, self).__init__(*args, **kwargs)

    def save(self):
        self.instance.quantity = self.cleaned_data['quantity']


class TestCartApp(app.CartApp):

    CART_SESSION_KEY = 'cart_token'
    Cart = MockCart
    CartItemForm = CartItemForm

    def get_cart_for_request(self, request):
        try:
            token = request.session[self.CART_SESSION_KEY]
            cart = self.Cart.instances[token]
        except KeyError:
            cart = self.Cart()
            request.session[self.CART_SESSION_KEY] = cart.token
        return cart


class TestCheckoutApp(CheckoutApp):

    Cart = MockCart
    Order = MockOrder
    def prepare_order(self, *args, **kwargs):
        return HttpResponse("OK")



product_app = TestProductApp()
checkout_app = TestCheckoutApp()
cart_app = TestCartApp()

class AppTestCase(ViewsTestCase):

    class urls:
        urlpatterns = patterns('',
            url(r'^cart/', include(cart_app.urls)),
            url(r'^products/', include(product_app.urls)),
            url(r'^checkout/', include(checkout_app.urls))
        )

    def setUp(self):
        test_dir = os.path.dirname(__file__)
        self.custom_settings = {
            'SATCHLESS_DEFAULT_CURRENCY': "PLN",
            'TEMPLATE_DIRS': [os.path.join(test_dir, 'templates'),
                              os.path.join(test_dir, '..', '..',
                                           'category', 'templates'),
                              os.path.join(test_dir, '..', 'templates')]
        }
        self.original_settings = self._setup_settings(self.custom_settings)
        pricing_handler.pricing_queue = pricing_handler.PricingQueue(FiveZlotyPriceHandler)

        self.cart = cart_app.Cart()
        self.variant_1 = MockProduct('macaw_blue')
        self.variant_2 = MockProduct('macaw_red')

    def tearDown(self):
        self._teardown_settings(self.original_settings,
                                self.custom_settings)

    def _get_or_create_cart_for_client(self, client=None, typ='cart'):
        client = client or self.client
        self._test_status(cart_app.reverse('details'), client_instance=client)
        cart_token = client.session[cart_app.CART_SESSION_KEY]
        return MockCart.instances[cart_token]

    def test_remove_item_by_view(self):
        cart = self._get_or_create_cart_for_client(self.client)
        cart.replace_item(self.variant_1, Decimal('2.45'))
        remove_item_url = cart_app.reverse('remove-item',
                                           args=(cart.get_all_items()[0].id,))
        response = self._test_status(remove_item_url, method='post',
                                     status_code=302,
                                     client_instance=self.client)
        self.assertRedirects(response, cart_app.reverse('details'))

    def test_cart_view_updates_item_quantity(self):
        cart = self._get_or_create_cart_for_client(self.client)

        cart.replace_item(self.variant_1, Decimal(1))
        response = self._test_status(cart_app.reverse('details'),
                                     client_instance=self.client,
                                     status_code=200)
        cart_item_form = response.context['cart_item_forms'][0]
        data = {
            'quantity': 2
        }
        data = dict((cart_item_form.add_prefix(key), value)
                    for (key, value) in data.items())
        self._test_status(cart_app.reverse('details'), data=data,
                          method='post', status_code=302,
                          client_instance=self.client)
        self.assertEqual(len(cart.get_all_items()), 1)
        self.assertEqual(cart.get_all_items()[0].quantity, 2)