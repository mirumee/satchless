# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.test import TestCase, Client
from django.db import models
from satchless.product.models import ProductAbstract
from .models import *

from decimal import Decimal

class DeadParrot(ProductAbstract):
    species = models.CharField(max_length=20)

class DeadParrotVariant(Variant):
    product = models.ForeignKey(DeadParrot, related_name='variants')
    color = models.CharField(max_length=10, choices=(('blue', 'blue'), ('white', 'white')))
    looks_alive = models.BooleanField()

    class Meta:
        unique_together = ('product', 'color', 'looks_alive')


class ParrotTest(TestCase):
    def setUp(self):
        self.macaw = DeadParrot.objects.create(slug='macaw',
                species="Hyacinth Macaw")
        self.cockatoo = DeadParrot.objects.create(slug='cockatoo',
                species="White Cockatoo")
        self.macaw_blue = self.macaw.variants.create(color='blue', looks_alive=False)
        self.macaw_blue_fake = self.macaw.variants.create(color='blue', looks_alive=True)
        self.cockatoo_white_a = self.cockatoo.variants.create(color='white', looks_alive=True)
        self.cockatoo_white_d = self.cockatoo.variants.create(color='white', looks_alive=False)
        self.cockatoo_blue_a = self.cockatoo.variants.create(color='blue', looks_alive=True)
        self.cockatoo_blue_d = self.cockatoo.variants.create(color='blue', looks_alive=False)
        self.user1 = User.objects.create(username="testuser")
        self.user1.set_password(u"pasło")
        self.user1.save()

    def _test_status(self, url, method='get', *args, **kwargs):
        status_code = kwargs.pop('status_code', 200)
        client = kwargs.pop('client_instance', Client())
        data = kwargs.pop('data', {})

        response = getattr(client, method)(url, data=data)
        self.assertEqual(response.status_code, status_code,
            'Incorrect status code for: %s, (%s, %s)! Expected: %s, received: %s. HTML:\n\n%s' % (
                url, args, kwargs, status_code, response.status_code, response.content
            )
        )
        return response

    def test_basic_cart_ops(self):
        cart = Cart.objects.create(typ='satchless.test_cart')
        cart.set_quantity(self.macaw_blue, 1)
        cart.set_quantity(self.macaw_blue_fake, Decimal('2.45'))
        cart.set_quantity(self.cockatoo_white_a, Decimal('2.45'))
        cart.set_quantity(self.cockatoo_white_d, 4.11)
        cart.set_quantity(self.cockatoo_blue_a, 6)
        cart.set_quantity(self.cockatoo_blue_d, Decimal('2'))
        cart.set_quantity(self.cockatoo_white_d, 0) # throw out
        cart.set_quantity(self.cockatoo_blue_a, Decimal('0')) # throw out
        cart.set_quantity(self.cockatoo_white_a, 0.0) # throw out

        self.assertEqual(cart.get_quantity(self.macaw_blue), Decimal('1'))
        self.assertEqual(cart.get_quantity(self.macaw_blue_fake), Decimal('2.45'))
        self.assertEqual(cart.get_quantity(self.cockatoo_white_a), 0) # thrown out
        self.assertRaises(CartItem.DoesNotExist, cart.items.get, variant=self.cockatoo_white_a)
        self.assertEqual(cart.get_quantity(self.cockatoo_white_d), Decimal('0')) # thrown out
        self.assertRaises(CartItem.DoesNotExist, cart.items.get, variant=self.cockatoo_white_d)
        self.assertEqual(cart.get_quantity(self.cockatoo_blue_a), 0.0) # thrown out
        self.assertRaises(CartItem.DoesNotExist, cart.items.get, variant=self.cockatoo_blue_a)
        self.assertEqual(cart.get_quantity(self.cockatoo_blue_d), Decimal('2'))

        cart.add_quantity(self.macaw_blue, 100)
        cart.add_quantity(self.macaw_blue_fake, 100)
        cart.add_quantity(self.cockatoo_white_a, 100)
        cart.add_quantity(self.cockatoo_white_d, 100)
        cart.add_quantity(self.cockatoo_blue_a, 100)
        cart.add_quantity(self.cockatoo_blue_d, 100)

        self.assertEqual(cart.get_quantity(self.macaw_blue), Decimal('101'))
        self.assertEqual(cart.get_quantity(self.macaw_blue_fake), Decimal('102.45'))
        self.assertEqual(cart.get_quantity(self.cockatoo_white_a), Decimal('100'))
        self.assertEqual(cart.get_quantity(self.cockatoo_white_d), Decimal('100'))
        self.assertEqual(cart.get_quantity(self.cockatoo_blue_a), Decimal('100'))
        self.assertEqual(cart.get_quantity(self.cockatoo_blue_d), Decimal('102'))

    def test_add_by_view(self):
        cli_anon = Client()
        cli_user1 = Client()
        self.assert_(cli_user1.login(username="testuser", password=u"pasło"))
        self._test_status(reverse('satchless-cart-view', kwargs={'typ': 'satchless.cart'}),
                client_instance=cli_anon, status_code=200)
        self._test_status(reverse('satchless-cart-view'), client_instance=cli_anon, status_code=200)
        self._test_status(reverse('satchless-cart-view', kwargs={'typ': 'satchless.cart'}),
                client_instance=cli_user1, status_code=200)

        self._test_status(reverse('satchless-cart-add', kwargs={'typ': 'satchless.cart'}),
                method='post',
                data={'variant': self.macaw_blue.pk, 'quantity': 1},
                client_instance=cli_user1,
                status_code=302)
        self._test_status(reverse('satchless-cart-add'),
                method='post',
                data={'variant': self.macaw_blue.pk, 'quantity': 1},
                client_instance=cli_anon,
                status_code=302)
