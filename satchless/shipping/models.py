from django.conf import settings
from django.db import models
from mothertongue.models import MothertongueModelTranslate

from ..util.models import Subtyped

class ShippingVariant(MothertongueModelTranslate, Subtyped):
    '''
    Base class for all shipping variants. This is what gets assigned to an
    order shipping group at the checkout step.
    '''
    name = models.CharField(_('name'), max_length=128)
    description = models.TextField(_('description'), blank=True)
    price = models.DecimalField(_('unit price'),
                                max_digits=12, decimal_places=4)
    def __unicode__(self):
        return self.name


class ShippingVariantTranslation(models.Model):
    language = models.CharField(max_length=5, choices=settings.LANGUAGES[1:])
    name = models.CharField(_('name'), max_length=128)
    description = models.TextField(_('description'), blank=True)

    def __unicode__(self):
        return "%s@%s" % (self.name, self.language)
