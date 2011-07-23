# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.test import TestCase

from ..util.tests import ViewTestCase
from ..product.tests import DeadParrot

from .models import Category
from .utils import get_product_url

__all__ = ['Views', 'Models']

class Models(TestCase):
    def test_paths(self):
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

class Views(ViewTestCase):
    def setUp(self):
        self.animals = Category.objects.create(slug='birds', name=u"Birds")
        self.birds = Category.objects.create(slug='birds', name=u"Birds",
                                             parent=self.category_animals)
        self.parrots = Category.objects.create(slug='parrots', name=u'Parrorts',
                                               parent=self.category_birds)

    def test_simple_views(self):
        self._test_GET_status(reverse('satchless-category-index'))
        self._test_GET_status(self.animals.get_absolute_url())
        self._test_GET_status(self.parrots.get_absolute_url())

    def test_category_product_view(self):
        parrot_macaw = DeadParrot.objects.create(slug='macaw', species="Hyacinth Macaw")
        self.parrots.products.add(parrot_macaw)
        self.birds.products.add(parrot_macaw)
        self._test_GET_status(get_product_url(parrot_macaw, self.birds))
        self._test_GET_status(get_product_url(parrot_macaw, self.parrots))


