from django.db import models
from django.utils.translation import ugettext_lazy as _

from satchless.product.models import ProductAbstract, Variant

class Book(ProductAbstract):
    author = models.TextField(_("author"), max_length=512)
    publisher = models.TextField(_("publisher"), max_length=300, blank=True)
    edition = models.PositiveIntegerField(_("edition"), null=True, blank=True)
    year = models.PositiveIntegerField(_("year"), null=True, blank=True)
    month = models.PositiveIntegerField(_("month"), null=True, blank=True)
    pages = models.PositiveIntegerField(_("number of pages"), blank=True)
    isbn = models.CharField(_("ISBN code"), max_length=13, blank=True)
    issn = models.CharField(_("ISSN code"), max_length=13, blank=True)

    class Meta:
        verbose_name = _("book")
        verbose_name_plural = _("books")


class BookVariant(Variant):
    product = models.ForeignKey(Book, related_name='variants')
    COVER_CHOICES = (
            ('soft', _("soft")), ('hard', _("hard")),
            ('hard_dust', _("hard with dust cover")),
            ('digital_pdf', _("digital, PDF")))
    cover = models.CharField(_("cover"), max_length=12, choices=COVER_CHOICES)

    class Meta:
        verbose_name = _("book variant")
        verbose_name_plural = _("book variants")
