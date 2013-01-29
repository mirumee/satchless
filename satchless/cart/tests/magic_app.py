# -*- coding: utf-8 -*-
from decimal import Decimal
from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.models import User
from django.test import Client
import os

from ...product.app import MagicProductApp
from ...product.tests import Parrot, ParrotVariant, DeadParrot, ZombieParrot, DeadParrotVariantForm
from ...util.tests import ViewsTestCase

from .. import app
from . import TestCart, TestCartItem


class TestProductApp(MagicProductApp):

    Product = Parrot
    Variant = ParrotVariant

product_app = TestProductApp()


class TestCartApp(app.MagicCartApp):

    app_name = 'test_cart_app'

    Cart = TestCart
    CartItem = TestCartItem

cart_app = TestCartApp(product_app)


class MagicAppTestCase(ViewsTestCase):

    class urls:
        urlpatterns = patterns('',
            url(r'^cart/', include(cart_app.urls)),
            url(r'^products/', include(product_app.urls)),
        )

    def setUp(self):
        self.macaw = DeadParrot.objects.create(slug='macaw',
                                               species='Hyacinth Macaw')
        self.cockatoo = DeadParrot.objects.create(slug='cockatoo',
                                                  species='White Cockatoo')
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
        # only staff users can view uncategorized products
        self.user1 = User.objects.create(username="testuser", is_staff=True,
                                         is_superuser=True)
        self.user1.set_password(u"pasło")
        self.user1.save()

        test_dir = os.path.dirname(__file__)
        self.custom_settings = {
            'SATCHLESS_DEFAULT_CURRENCY': "PLN",
            'TEMPLATE_DIRS': [os.path.join(test_dir, 'templates'),
                              os.path.join(test_dir, '..', '..',
                                           'category', 'templates'),
                              os.path.join(test_dir, '..', 'templates'),
                              os.path.join(test_dir, 'templates')]
        }
        self.original_settings = self._setup_settings(self.custom_settings)

    def tearDown(self):
        self._teardown_settings(self.original_settings,
                                self.custom_settings)

    def _get_or_create_cart_for_client(self, client=None):
        client = client or self.client
        self._test_status(cart_app.reverse('details'), client_instance=client)
        cart_token = client.session[cart_app.cart_session_key]
        return cart_app.Cart.objects.get(token=cart_token)

    def test_add_to_cart_form_on_product_view(self):
        response = self._test_status(self.macaw.get_absolute_url(),
                                     method='get', status_code=200)
        self.assertTrue(isinstance(response.context['product'].cart_form,
                        DeadParrotVariantForm))

        zombie = ZombieParrot.objects.create(slug='zombie-parrot',
                                             species='Zombie Parrot')
        response = self._test_status(zombie.get_absolute_url(),
                                     method='get', status_code=200)
        self.assertTrue(isinstance(response.context['product'].cart_form,
                        DeadParrotVariantForm))

    def _test_add_by_view(self, client):
        cart = self._get_or_create_cart_for_client(client)
        self._test_status(cart_app.reverse('details'),
                          client_instance=client, status_code=200)
        self._test_status(self.macaw.get_absolute_url(),
                          method='post',
                          data={'target': cart.token,
                                'color': self.macaw_blue_fake.color,
                                'looks_alive': self.macaw_blue_fake.looks_alive,
                                'quantity': 2},
                          client_instance=client,
                          status_code=302)
        self.assertEqual(cart.items.count(), 1)
        cart_item = cart.items.get()
        self.assertEqual(cart_item.quantity, 2)
        self.assertEqual(self.macaw_blue_fake,
                         cart_item.variant.get_subtype_instance())

    def test_remove_item_by_view(self):
        cart = self._get_or_create_cart_for_client(self.client)
        cart.replace_item(self.macaw_blue_fake, Decimal('2.45'))
        remove_item_url = cart_app.reverse('remove-item',
                                           args=(cart.items.get().id,))
        response = self._test_status(remove_item_url, method='post',
                                     status_code=302,
                                     client_instance=self.client)
        self.assertRedirects(response, cart_app.reverse('details'))

    def test_cart_view_with_item(self):
        cart = self._get_or_create_cart_for_client(self.client)
        cart.replace_item(self.macaw_blue_fake, Decimal('2.45'))
        self._test_status(cart_app.reverse('details'),
                          client_instance=self.client, status_code=200)

    def test_cart_view_updates_item_quantity(self):
        cart = self._get_or_create_cart_for_client(self.client)
        cart.replace_item(self.macaw_blue_fake, Decimal(1))
        response = self._test_status(cart_app.reverse('details'),
                                     client_instance=self.client,
                                     status_code=200)
        cart_item_form = response.context['cart_item_forms'][0]
        data = {
            'quantity': 2,
        }
        data = dict((cart_item_form.add_prefix(key), value)
                    for (key, value) in data.items())
        self._test_status(cart_app.reverse('details'), data=data,
                          method='post', status_code=302,
                          client_instance=self.client)
        self.assertEqual(cart.items.count(), 1)
        self.assertEqual(cart.items.get().quantity, 2)

    def test_add_by_view_for_anonymous(self):
        cli_anon = Client()
        self._test_add_by_view(cli_anon)

    def test_add_by_view(self):
        cli_user1 = Client()
        self.assertTrue(cli_user1.login(username="testuser", password=u"pasło"))
        self._test_add_by_view(cli_user1)

    def test_add_to_cart_form_handles_incorrect_data(self):
        cli_anon = Client()
        cart = self._get_or_create_cart_for_client(cli_anon)
        response = self._test_status(self.macaw.get_absolute_url(),
                                     method='post',
                                     data={'target': cart.token,
                                           'color': 'blue',
                                           'looks_alive': 1,
                                           'quantity': 'alkjl'},
                                     client_instance=cli_anon,
                                     status_code=200)
        errors = response.context['product'].cart_form.errors
        self.assertTrue('quantity' in errors)

