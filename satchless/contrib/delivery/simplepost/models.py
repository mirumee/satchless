from django.db import models
from django.utils.translation import ugettext_lazy as _


class PostShippingType(models.Model):
    typ = models.SlugField(max_length=50, unique=True)
    name = models.CharField(_('name'), max_length=128)
    price = models.DecimalField(_('price'), max_digits=10, decimal_places=2)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Post shipping type')
        verbose_name_plural = _('Post shipping types')


