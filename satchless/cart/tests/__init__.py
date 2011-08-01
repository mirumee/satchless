# -*- coding: utf-8 -*-
from decimal import Decimal
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase, Client
from django import forms
import os

from ...product.forms import BaseVariantForm
from ...product import handler
from ...product.signals import variant_formclass_for_product
from ...product.tests import DeadParrot, DeadParrotVariant
from .. import models
from .. import signals

class DeadParrotVariantForm(BaseVariantForm):
    color = forms.CharField(max_length=10)
    looks_alive = forms.BooleanField()

    def _get_variant_queryset(self):
        return DeadParrotVariant.objects.filter(
                product=self.product,
                color=self.cleaned_data['color'],
                looks_alive=self.cleaned_data['looks_alive'])

    def clean(self):
        if not self._get_variant_queryset().exists():
            raise forms.ValidationError("Variant does not exist")
        return self.cleaned_data

    def get_variant(self):
        return self._get_variant_queryset().get()


def get_variantformclass(sender=None, instance=None, formclass=None, **kwargs):
    formclass.append(DeadParrotVariantForm)

variant_formclass_for_product.connect(get_variantformclass, sender=DeadParrot)


class ParrotTest(TestCase):
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
        self.ORIGINAL_TEMPLATE_DIRS = settings.TEMPLATE_DIRS
        settings.TEMPLATE_DIRS = [os.path.join(os.path.dirname(__file__),
                                               'templates')]
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
        # only staff users can view uncategorized products
        self.user1 = User.objects.create(username="testuser", is_staff=True,
                                         is_superuser=True)
        self.user1.set_password(u"pasło")
        self.user1.save()
        self.custom_settings = {
            'SATCHLESS_PRODUCT_VIEW_HANDLERS': ('satchless.cart.add_to_cart_handler',),
        }
        self.original_settings = self._setup_settings(self.custom_settings)
        handler.init_queue()

    def tearDown(self):
        settings.TEMPLATE_DIRS = self.ORIGINAL_TEMPLATE_DIRS
        self._teardown_settings(self.original_settings, self.custom_settings)
        handler.init_queue()

    def _test_status(self, url, method='get', *args, **kwargs):
        status_code = kwargs.pop('status_code', 200)
        client = kwargs.pop('client_instance', Client())
        data = kwargs.pop('data', {})

        response = getattr(client, method)(url, data=data)
        self.assertEqual(response.status_code, status_code,
                         'Incorrect status code for: %s, (%s, %s)!'
                         ' Expected: %s, received: %s. HTML:\n\n%s' %
                         (url.decode('utf-8'), args, kwargs, status_code,
                          response.status_code,
                          response.content.decode('utf-8')))
        return response

    def test_basic_cart_ops(self):
        cart = models.Cart.objects.create(typ='satchless.test_cart')
        cart.set_quantity(self.macaw_blue, 1)
        cart.set_quantity(self.macaw_blue_fake, Decimal('2.45'))
        cart.set_quantity(self.cockatoo_white_a, Decimal('2.45'))
        cart.set_quantity(self.cockatoo_white_d, '4.11')
        cart.set_quantity(self.cockatoo_blue_a, 6)
        cart.set_quantity(self.cockatoo_blue_d, Decimal('2'))
        # remove three items
        cart.set_quantity(self.cockatoo_white_d, 0)
        cart.set_quantity(self.cockatoo_blue_a, Decimal('0'))
        cart.set_quantity(self.cockatoo_white_a, '0.0')

        self.assertEqual(cart.get_quantity(self.macaw_blue), Decimal('1'))
        self.assertEqual(cart.get_quantity(self.macaw_blue_fake), Decimal('2'))
        self.assertEqual(cart.get_quantity(self.cockatoo_white_a), 0)
        self.assertRaises(models.CartItem.DoesNotExist, cart.items.get,
                          variant=self.cockatoo_white_a)
        self.assertEqual(cart.get_quantity(self.cockatoo_white_d), Decimal('0'))
        self.assertRaises(models.CartItem.DoesNotExist, cart.items.get,
                          variant=self.cockatoo_white_d)
        self.assertEqual(cart.get_quantity(self.cockatoo_blue_a), Decimal('0.0'))
        self.assertRaises(models.CartItem.DoesNotExist, cart.items.get,
                          variant=self.cockatoo_blue_a)
        self.assertEqual(cart.get_quantity(self.cockatoo_blue_d), Decimal('2'))

        cart.add_quantity(self.macaw_blue, 100)
        cart.add_quantity(self.macaw_blue_fake, 100)
        cart.add_quantity(self.cockatoo_white_a, 100)
        cart.add_quantity(self.cockatoo_white_d, 100)
        cart.add_quantity(self.cockatoo_blue_a, 100)
        cart.add_quantity(self.cockatoo_blue_d, 100)

        self.assertEqual(cart.get_quantity(self.macaw_blue), Decimal('101'))
        self.assertEqual(cart.get_quantity(self.macaw_blue_fake), Decimal('102'))
        self.assertEqual(cart.get_quantity(self.cockatoo_white_a), Decimal('100'))
        self.assertEqual(cart.get_quantity(self.cockatoo_white_d), Decimal('100'))
        self.assertEqual(cart.get_quantity(self.cockatoo_blue_a), Decimal('100'))
        self.assertEqual(cart.get_quantity(self.cockatoo_blue_d), Decimal('102'))

    def test_add_by_view(self):
        cli_anon = Client()
        cli_user1 = Client()
        self.assert_(cli_user1.login(username="testuser", password=u"pasło"))
        # We also test different ways of URL resolving here
        self._test_status(reverse('satchless-cart-view'),
                          client_instance=cli_anon, status_code=200)
        self._test_status(reverse('satchless-cart-view'),
                          client_instance=cli_anon, status_code=200)
        self._test_status(reverse('satchless-cart-view'),
                          client_instance=cli_user1, status_code=200)

        self._test_status(reverse('satchless-product-details',
                                  args=(self.macaw.pk, self.macaw.slug)),
                          method='post',
                          data={'typ': 'satchless_cart',
                                'color': 'blue',
                                'looks_alive': 1,
                                'quantity': 1},
                          client_instance=cli_anon,
                          status_code=302)
        self._test_status(reverse('satchless-product-details',
                                  args=(self.cockatoo.pk, self.cockatoo.slug)),
                          method='post',
                          data={'typ': 'satchless_cart',
                                'color': 'white',
                                'looks_alive': 1,
                                'quantity': 10},
                          client_instance=cli_user1,
                          status_code=302)

    def test_add_to_cart_form_handles_incorrect_data(self):
        cli_anon = Client()
        response = self._test_status(reverse('satchless-product-details',
                                             args=(self.macaw.pk, self.macaw.slug)),
                                     method='post',
                                     data={'typ': 'satchless_cart',
                                           'color': 'blue',
                                           'looks_alive': 1,
                                           'quantity': 'alkjl'},
                                     client_instance=cli_anon,
                                     status_code=200)
        self.assertTrue('quantity' in response.context['product'].cart_form.errors)

    def test_signals(self):
        def modify_qty(sender, instance=None, variant=None,
                old_quantity=None, new_quantity=None, result=None, **kwargs):
            if instance.typ != 'satchless.test_cart_with_signals':
                return
            if variant.product == self.macaw:
                result.append((Decimal('0'), u"Out of stock"))
            elif not variant.looks_alive:
                result.append((Decimal('1'), u"Parrots don't rest in groups"))

        cart = models.Cart.objects.create(typ='satchless.test_cart_with_signals')
        signals.cart_quantity_change_check.connect(modify_qty)
        result = cart.set_quantity(self.macaw_blue, 10, dry_run=True)
        self.assertEqual((result.new_quantity, result.reason),
                         (0, u"Out of stock"))
        self.assertEqual(0, cart.get_quantity(self.macaw_blue))
        result = cart.set_quantity(self.macaw_blue, 10)
        self.assertEqual((result.new_quantity, result.reason),
                         (0, u"Out of stock"))
        self.assertEqual(0, cart.get_quantity(self.macaw_blue))
        result = cart.add_quantity(self.macaw_blue, 10)
        self.assertEqual((result.new_quantity, result.quantity_delta,
                          result.reason),
                         (0, 0, u"Out of stock"))
        self.assertEqual(0, cart.get_quantity(self.macaw_blue))
        result = cart.set_quantity(self.cockatoo_white_d, 10, dry_run=True)
        self.assertEqual((result.new_quantity, result.reason),
                         (1, u"Parrots don't rest in groups"))
        self.assertEqual(0, cart.get_quantity(self.cockatoo_white_d))
        result = cart.set_quantity(self.cockatoo_white_d, 10)
        self.assertEqual((result.new_quantity, result.reason),
                         (1, u"Parrots don't rest in groups"))
        self.assertEqual(1, cart.get_quantity(self.cockatoo_white_d))
        result = cart.add_quantity(self.cockatoo_white_d, 10)
        self.assertEqual((result.new_quantity,
                          result.quantity_delta,
                          result.reason),
                         (1, 0, u"Parrots don't rest in groups"))
        self.assertEqual(1, cart.get_quantity(self.cockatoo_white_d))
