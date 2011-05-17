# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.test import TestCase, Client

from ..models import Category, Variant, ProductAbstract

__all__ = [ 'ParrotTest' ]
from . import DeadParrot, DeadParrotVariant

class ParrotTest(TestCase):
    def setUp(self):
        self.birds = Category.objects.create(slug='birds', name=u"Birds")
        self.parrots = Category.objects.create(slug='parrots',
                name=u"Parrots", parent=self.birds)
        self.storks = Category.objects.create(slug='storks',
                name=u"Storks", parent=self.birds)
        self.macaw = DeadParrot.objects.create(slug='macaw',
                species="Hyacinth Macaw")
        self.cockatoo = DeadParrot.objects.create(slug='cockatoo',
                species="White Cockatoo")
        self.macaw.categories.add(self.parrots)
        self.cockatoo.categories.add(self.parrots)

        self.client_test = Client()

    def test_paths(self):
        self.assertRaises(ValueError,
                self.macaw.get_absolute_url,
                category=self.storks)
        forks = Category.objects.create(slug='forks', name=u"Forks", parent=self.storks)
        Category.objects.create(slug='porks', name=u"Porks", parent=forks)
        borks = Category.objects.create(slug='borks', name=u"Borks", parent=forks)
        forks2 = Category.objects.create(slug='forks', name=u"Forks", parent=borks)
        yorks = Category.objects.create(slug='yorks', name=u"Yorks", parent=forks2)
        Category.objects.create(slug='orcs', name=u"Orcs", parent=forks2)
        self.assertEqual(
                [self.birds, self.storks, forks],
                Category.path_from_slugs(['birds', 'storks', 'forks']))
        self.assertEqual(
                [self.birds, self.storks, forks, borks, forks2],
                Category.path_from_slugs(['birds', 'storks', 'forks', 'borks', 'forks']))
        self.assertRaises(
                Category.DoesNotExist,
                Category.path_from_slugs,
                (['birds', 'storks', 'borks', 'forks']))
        self.assertEqual(
                [self.birds, self.storks, forks, borks, forks2, yorks],
                Category.path_from_slugs(['birds', 'storks', 'forks', 'borks', 'forks', 'yorks']))
        self.assertRaises(
                Category.DoesNotExist,
                Category.path_from_slugs,
                (['birds', 'storks', 'forks', 'porks', 'forks', 'yorks']))

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

    def _test_status(self, url, method='get', *args, **kwargs):
        status_code = kwargs.pop('status_code', 200)
        client = kwargs.pop('client_instance', self.client_test)
        data = kwargs.pop('data', {})

        response = getattr(client, method)(url, data=data)
        self.assertEqual(response.status_code, status_code,
            'Incorrect status code for: %s, (%s, %s)! Expected: %s, received: %s. HTML:\n\n%s' % (
                url.decode('utf-8'), args, kwargs, status_code, response.status_code,
                response.content.decode('utf-8')
            )
        )
        return response

    def test_simple_views(self):
        self._test_status(reverse('satchless.product.views.index'))
        self._test_status(self.birds.get_absolute_url())
        self._test_status(self.parrots.get_absolute_url())
        self._test_status(self.macaw.get_absolute_url())
        self._test_status(self.macaw.get_absolute_url(category=self.parrots))
        self._test_status(
                self.macaw.get_absolute_url(category=self.parrots).replace('parrots', 'storks'),
                status_code=404
                )
