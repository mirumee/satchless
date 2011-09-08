from django.core.urlresolvers import reverse

from ..util.tests import ViewTestCase
from ..product.tests import DeadParrot

from .models import Category
from .app import product_app

__all__ = ('Views',)

class Views(ViewTestCase):
    def setUp(self):
        self.animals = Category.objects.create(slug='birds', name=u'Birds')
        self.birds = Category.objects.create(slug='birds', name=u'Birds',
                                             parent=self.animals)
        self.parrots = Category.objects.create(slug='parrots', name=u'Parrorts',
                                               parent=self.birds)

    def test_category_list(self):
        self._test_GET_status(reverse('satchless-category-list'))

    def test_category_details(self):
        response = self._test_GET_status(self.animals.get_absolute_url())
        self.assertTrue('category' in response.context)
        self.assertEqual(response.context['category'], self.animals)

        response = self._test_GET_status(self.parrots.get_absolute_url())
        self.assertTrue('category' in response.context)
        self.assertEqual(response.context['category'], self.parrots)

    def test_category_product_view(self):
        parrot_macaw = DeadParrot.objects.create(slug='macaw', species='Hyacinth Macaw')
        self.animals.products.add(parrot_macaw)
        self.parrots.products.add(parrot_macaw)
        response = self._test_GET_status(parrot_macaw.get_absolute_url(category=self.animals))
        self.assertTrue('product' in response.context)
        self.assertEqual(response.context['product'], parrot_macaw)

        self._test_GET_status(parrot_macaw.get_absolute_url(category=self.parrots))
        self.assertTrue('product' in response.context)
        self.assertEqual(response.context['product'], parrot_macaw)

    def test_paths(self):
        birds = Category.objects.create(slug='birds', name=u'Birds')
        storks = Category.objects.create(slug='storks', name=u'Storks', parent=birds)
        forks = Category.objects.create(slug='forks', name=u'Forks', parent=storks)
        Category.objects.create(slug='porks', name=u'Porks', parent=forks)
        borks = Category.objects.create(slug='borks', name=u'Borks', parent=forks)
        forks2 = Category.objects.create(slug='forks', name=u'Forks', parent=borks)
        yorks = Category.objects.create(slug='yorks', name=u'Yorks', parent=forks2)
        Category.objects.create(slug='orcs', name=u'Orcs', parent=forks2)
        self.assertEqual(
                [birds, storks, forks],
                product_app.path_from_slugs(['birds', 'storks', 'forks']))
        self.assertEqual(
                [birds, storks, forks, borks, forks2],
                product_app.path_from_slugs(['birds', 'storks', 'forks', 'borks', 'forks']))
        self.assertRaises(
                Category.DoesNotExist,
                product_app.path_from_slugs,
                (['birds', 'storks', 'borks', 'forks']))
        self.assertEqual(
                [birds, storks, forks, borks, forks2, yorks],
                product_app.path_from_slugs(['birds', 'storks', 'forks', 'borks', 'forks', 'yorks']))
        self.assertRaises(
                Category.DoesNotExist,
                product_app.path_from_slugs,
                (['birds', 'storks', 'forks', 'porks', 'forks', 'yorks']))
