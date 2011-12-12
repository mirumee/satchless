from django.db import models
from django.utils.translation import ugettext_lazy as _
from mptt.models import MPTTModel, TreeManager

__all__ = ('Category', 'CategoryManager')

class CategoryManager(TreeManager):

    def get_product_url(self, product, category):
        if not category:
            if not product.categories.exists():
                raise ValueError('Cannot generate url for product'
                                 ' without categories')
            category = product.categories.all()[0]
        return ('product:details',
                ('%s%s/' % (category.parents_slug_path(),
                            category.slug),
                 product.slug))


class Category(MPTTModel):

    name = models.CharField(_('name'), max_length=128)
    description = models.TextField(_('description'), blank=True)
    meta_description = models.TextField(_('meta description'), blank=True,
            help_text=_("Description used by search and indexing engines"))
    slug = models.SlugField(max_length=50)
    parent = models.ForeignKey('self', null=True, blank=True,
                               related_name='children')

    objects = CategoryManager()

    class Meta:
        abstract = True
        verbose_name = _("category")
        verbose_name_plural = _("categories")

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('product:category-details',
                (self.parents_slug_path(), self.slug))

    def parents_slug_path(self):
        parents = '/'.join(c.slug for c in self.get_ancestors())
        return '%s/' % parents if parents else ''
