from django.db import models
from django.utils.translation import ugettext_lazy as _

from mptt.models import MPTTModel

__all__ = ('ProductAbstract', 'Variant', 'Category')

class DescribedModel(models.Model):
    name = models.CharField(_('name'), max_length=128)
    description = models.TextField(_('description'), max_length=16*1024, blank=True)
    meta_description = models.TextField(_('meta description'), max_length=2*1024, blank=True,
            help_text=_("Description used by search and indexing engines"))

    def __unicode__(self):
        return self.name

    class Meta:
        abstract = True


class Category(MPTTModel, DescribedModel):
    slug = models.SlugField(max_length=50)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children')

    def _parents_slug_path(self):
        parents = '/'.join(map(lambda c: c.slug, self.get_ancestors()))
        return '%s/' % parents if parents else ''

    @staticmethod
    def path_from_slugs(slugs):
        if len(slugs) == 0:
            return []
        leaves = Category.objects.filter(slug=slugs[-1])
        if not leaves:
            raise Category.DoesNotExist, "slug='%s'" % slugs[-1]
        for leaf in leaves:
            path = leaf.get_ancestors()
            if len(path) + 1 != len(slugs):
                continue
            if map(lambda c: c.slug, path) != slugs[:-1]:
                continue
            return list(path) + [leaf]
        raise Category.DoesNotExist

    @models.permalink
    def get_absolute_url(self):
        return ('satchless.product.views.category', (self._parents_slug_path(), self.slug))

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

class Product(models.Model):
    """The base Product to rule them all. Provides slug, a powerful item to
    identify member of each tribe."""
    slug = models.SlugField(max_length=80)
    categories = models.ManyToManyField(Category, related_name='products')

    @models.permalink
    def get_absolute_url(self, category=None):
        if category:
            if self.categories.filter(pk=category.pk).count():
                return ('satchless.product.views.product', (
                    '%s%s/' % (category._parents_slug_path(), category.slug),
                    self.slug))
            else:
                raise ValueError, _("Product %s not in category %s") % (self, category)
        return ('satchless.product.views.product', (self.slug,))

    def __unicode__(self):
        return self.slug


class ProductAbstract(Product, DescribedModel):
    """Base class for every product to inherit from."""

    class Meta:
        abstract = True


class Variant(models.Model):
    """A base class for variants. It identifies a concrete product instance,
    which goes to a cart. Custom variants inherit from it."""
    pass