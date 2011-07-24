# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, include, url
from django.core.urlresolvers import reverse
from django.test import TestCase, Client

from ..models import Variant, ProductAbstract
from ..app import product_app

from . import DeadParrot, DeadParrotVariant

__all__ = ['Models', 'Views']

urlpatterns = patterns('',
    url(r'^cart/', include(product_app.urls)),
)

class Models(TestCase):
    def setUp(self):
        self.macaw = DeadParrot.objects.create(slug='macaw',
                species="Hyacinth Macaw")
        self.cockatoo = DeadParrot.objects.create(slug='cockatoo',
                species="White Cockatoo")
        self.client_test = Client()

    def test_product_subclass_promotion(self):
        for product in ProductAbstract.objects.all():
            # test saving as base and promoted class
            self.assertEqual(type(product.get_subtype_instance()), DeadParrot)
            ProductAbstract.objects.get(pk=product.pk).save()
            self.assertEqual(type(product.get_subtype_instance()), DeadParrot)
            DeadParrot.objects.get(pk=product.pk).save()
            self.assertEqual(type(product.get_subtype_instance()), DeadParrot)

    def test_variants(self):
        self.macaw.variants.create(color='blue', looks_alive=False)
        self.macaw.variants.create(color='blue', looks_alive=True)
        self.assertEqual(2, self.macaw.variants.count())

        self.cockatoo.variants.create(color='white', looks_alive=True)
        self.cockatoo.variants.create(color='white', looks_alive=False)
        self.cockatoo.variants.create(color='blue', looks_alive=True)
        self.cockatoo.variants.create(color='blue', looks_alive=False)
        self.assertEqual(4, self.cockatoo.variants.count())

        for variant in Variant.objects.all():
            # test saving as base and promoted class
            self.assertEqual(type(variant.get_subtype_instance()), DeadParrotVariant)
            Variant.objects.get(pk=variant.pk).save()
            self.assertEqual(type(variant.get_subtype_instance()), DeadParrotVariant)
            DeadParrotVariant.objects.get(pk=variant.pk).save()
            self.assertEqual(type(variant.get_subtype_instance()), DeadParrotVariant)


class Views(TestCase):
    urls = 'satchless.product.tests.product'

    def setUp(self):
        self.macaw = DeadParrot.objects.create(slug='macaw',
                species="Hyacinth Macaw")
        self.client_test = Client()

    def test_product_details_view(self):
        response = self.client.get(reverse('satchless-product-details',
                                           args=(self.macaw.pk, self.macaw.slug)))
        self.assertEqual(response.status_code, 200)
