from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _
from mptt.models import MPTTModel

from ..util.models import DeferredManyToManyField

__all__ = ('Category', 'CategorizedProduct')


class Category(MPTTModel):

    name = models.CharField(_('name'), max_length=128)
    description = models.TextField(_('description'), blank=True)
    meta_description = models.TextField(_('meta description'), blank=True,
            help_text=_("Description used by search and indexing engines"))
    slug = models.SlugField(max_length=50)
    parent = models.ForeignKey('self', null=True, blank=True,
                               related_name='children')

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


class CategorizedProductMixin(models.Model):

    categories = DeferredManyToManyField('category',
                                         related_name='products',
                                         null=True)

    class Meta:
        abstract = True

    def get_categories(self):
        return self.categories.all()

    def get_absolute_url(self, category=None):
        if category or self.get_categories().exists():
            if not category:
                category = self.categories.all()[0]
            args = ('%s%s/' % (category.parents_slug_path(),
                               category.slug),
                    self.pk, self.slug)

            return reverse('product:details', args=args)
        return super(CategorizedProductMixin, self).get_absolute_url()
