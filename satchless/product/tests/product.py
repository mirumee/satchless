# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.core.urlresolvers import reverse
from django.db import connection, reset_queries
from django.test import TestCase, Client

from ..forms import FormRegistry, variant_form_for_product
from ..models import Variant, Product
from ..app import product_app

from . import DeadParrot, DeadParrotVariant, ZombieParrot, DeadParrotVariantForm

__all__ = ['Models', 'Registry', 'Views']

urlpatterns = patterns('',
    url(r'^products/', include(product_app.urls)),
)

class Models(TestCase):
    urls = 'satchless.product.tests.product'

    def setUp(self):
        settings.DEBUG = True
        self.macaw = DeadParrot.objects.create(slug='macaw',
                species='Hyacinth Macaw')
        self.cockatoo = DeadParrot.objects.create(slug='cockatoo',
                species='White Cockatoo')
        self.client_test = Client()

    #def test_subtype_performance(self):
    #    reset_queries()
    #    product = Product.objects.get(slug='macaw')
    #    product.get_subtype_instance()
    #    self.assertEqual(len(connection.queries), 1)

    def test_product_subclass_promotion(self):
        for product in Product.objects.all():
            # test saving as base and promoted class
            self.assertEqual(type(product.get_subtype_instance()), DeadParrot)
            Product.objects.get(pk=product.pk).save()
            self.assertEqual(type(product.get_subtype_instance()), DeadParrot)
            DeadParrot.objects.get(pk=product.pk).save()
            self.assertEqual(type(product.get_subtype_instance()), DeadParrot)

    def test_variants(self):
        self.macaw.variants.create(color='blue', sku='M-BL-D',
                                   looks_alive=False)
        self.macaw.variants.create(color='blue', sku='M-BL-A', looks_alive=True)
        self.assertEqual(2, self.macaw.variants.count())

        self.cockatoo.variants.create(color='white', sku='C-WH-A',
                                      looks_alive=True)
        self.cockatoo.variants.create(color='white', sku='C-WH-D',
                                      looks_alive=False)
        self.cockatoo.variants.create(color='blue', sku='C-BL-A',
                                      looks_alive=True)
        self.cockatoo.variants.create(color='blue', sku='C-BL-D',
                                      looks_alive=False)
        self.assertEqual(4, self.cockatoo.variants.count())

        for variant in Variant.objects.all():
            # test saving as base and promoted class
            self.assertEqual(type(variant.get_subtype_instance()), DeadParrotVariant)
            Variant.objects.get(pk=variant.pk).save()
            self.assertEqual(type(variant.get_subtype_instance()), DeadParrotVariant)
            DeadParrotVariant.objects.get(pk=variant.pk).save()
            self.assertEqual(type(variant.get_subtype_instance()), DeadParrotVariant)

    def test_product_url(self):
        self.assertEqual('/products/+1-macaw/', self.macaw.get_absolute_url())


class Registry(TestCase):
    def test_form_registry(self):
        registry = FormRegistry()
        variant_form_for_product(DeadParrot,
                                 registry=registry)(DeadParrotVariantForm)
        self.assertEqual(registry.get_handler(DeadParrot),
                         DeadParrotVariantForm)
        self.assertEqual(registry.get_handler(ZombieParrot),
                         DeadParrotVariantForm)


class Views(TestCase):
    urls = 'satchless.product.tests.product'

    def setUp(self):
        self.macaw = DeadParrot.objects.create(slug='macaw',
                species='Hyacinth Macaw')
        self.client_test = Client()

    def test_product_details_view(self):
        response = self.client.get(reverse('satchless-product-details',
                                           args=(self.macaw.pk, self.macaw.slug)))
        self.assertEqual(response.status_code, 200)