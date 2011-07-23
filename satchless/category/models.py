# -*- coding:utf-8 -*-
from django.db import models, manager
from django.utils.translation import ugettext as _
from mptt.models import MPTTModel

from ..product.models import Product

__all__ = ('Category',)

class CategoryManager(manager.Manager):
    def path_from_slugs(self, slugs):
        """
        Returns list of Category instances matchnig given slug path.
        """
        if len(slugs) == 0:
            return []
        leaves = self.get_query_set().filter(slug=slugs[-1])
        if not leaves:
            raise Category.DoesNotExist, "slug='%s'" % slugs[-1]
        for leaf in leaves:
            path = leaf.get_ancestors()
            if len(path) + 1 != len(slugs):
                continue
            if [c.slug for c in path] != slugs[:-1]:
                continue
            return list(path) + [leaf]
        raise Category.DoesNotExist


class Category(MPTTModel):
    name = models.CharField(_('name'), max_length=128)
    description = models.TextField(_('description'), blank=True)
    meta_description = models.TextField(_('meta description'), blank=True,
            help_text=_("Description used by search and indexing engines"))
    slug = models.SlugField(max_length=50)
    parent = models.ForeignKey('self', null=True, blank=True,
                               related_name='children')
    products = models.ManyToManyField(Product, related_name='categories')

    objects = CategoryManager()

    class Meta:
        verbose_name = _("category")
        verbose_name_plural = _("categories")

    def __unicode__(self):
        return self.name

    def parents_slug_path(self):
        parents = '/'.join(c.slug for c in self.get_ancestors())
        return '%s/' % parents if parents else ''

    @models.permalink
    def get_absolute_url(self):
        return ('satchless.product.views.category',
                (self.parents_slug_path(), self.slug))

