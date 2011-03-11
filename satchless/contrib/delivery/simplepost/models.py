from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from satchless.delivery.models import PhysicalShippingVariant
from mothertongue.models import MothertongueModelTranslate

class PostShippingType(MothertongueModelTranslate):
    typ = models.SlugField(max_length=50, unique=True)
    name = models.CharField(_('name'), max_length=128)
    price = models.DecimalField(_('price'), max_digits=10, decimal_places=2)
    translated_fields = ('name',)
    translation_set = 'translations'

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Post shipping type')
        verbose_name_plural = _('Post shipping types')


class PostShippingTypeTranslation(models.Model):
    postshippingtype = models.ForeignKey(PostShippingType, related_name='translations')
    language = models.CharField(max_length=5, choices=settings.LANGUAGES[1:])
    name = models.CharField(_('name'), max_length=128)

    def __unicode__(self):
        return "%s@%s" % (self.name, self.language)


class PostShippingVariant(PhysicalShippingVariant):
    pass
