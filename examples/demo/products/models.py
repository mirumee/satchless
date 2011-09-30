# -*- coding:utf-8 -*-
import os

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _
from mothertongue.models import MothertongueModelTranslate
from satchless.image.models import Image
import satchless.product.models

class ProductImage(Image):
    product = models.ForeignKey(satchless.product.models.Product, related_name="images")
    caption = models.CharField(_("Caption"), max_length=128, blank=True)
    order = models.PositiveIntegerField(blank=True)

    class Meta:
        ordering = ('order',)

    def __unicode__(self):
        return os.path.basename(self.image.name)

    def save(self, *args, **kwargs):
        if self.order is None:
            self.order = self.product.images.aggregate(max_order=models.Max("order"))['max_order'] or 0
        return super(ProductImage, self).save(*args, **kwargs)


class Make(models.Model):
    name = models.TextField(_("manufacturer"), default='', blank=True)
    logo = models.ImageField(upload_to="make/logo/")

    def __unicode__(self):
        return self.name


class Product(MothertongueModelTranslate, satchless.product.models.ProductAbstract):
    make = models.ForeignKey(Make, null=True, blank=True, on_delete=models.SET_NULL,
        help_text=_("Product manufacturer"))
    main_image = models.ForeignKey(ProductImage, null=True, blank=True, on_delete=models.SET_NULL,
            help_text=_("Main product image (first image by default)"))
    translated_fields = ('name', 'description', 'meta_description', 'manufacture')
    translation_set = 'translations'

    class Meta:
        abstract = True


class ProductTranslation(models.Model):
    language = models.CharField(max_length=5, choices=settings.LANGUAGES[1:])
    name = models.CharField(_('name'), max_length=128)
    description = models.TextField(_('description'), blank=True)
    manufacture = models.TextField(_("Manufacture"), default='', blank=True)
    meta_description = models.TextField(_('meta description'), blank=True,
            help_text=_("Description used by search and indexing engines"))

    class Meta:
        abstract = True

    def __unicode__(self):
        return "%s@%s" % (self.name, self.language)


class ColoredVariant(satchless.product.models.Variant):
    COLOR_CHOICES = (('red', _("Red")), ('green', _("Green")), ('blue', _("Blue")))
    color = models.CharField(max_length=32, choices=COLOR_CHOICES)
    class Meta:
        abstract = True


class Cardigan(Product):
    class Meta:
        verbose_name = _('Cardigan')
        verbose_name_plural = _('Cardigans')


class CardiganTranslation(ProductTranslation):
    product = models.ForeignKey(Cardigan, related_name='translation')


class CardiganVariant(ColoredVariant):
    product = models.ForeignKey(Cardigan, related_name='variants')
    SIZE_CHOICES = (('S', 'S'), ('XS', 'XS'), ('M', 'M'), ('L', 'L'), ('XL', 'XL'))
    size = models.CharField(choices=SIZE_CHOICES, max_length=2)

    def __unicode__(self):
        return '%s (%s / %s)' % (self.product, self.get_color_display(), self.get_size_display())


class Dress(Product):
    class Meta:
        verbose_name = _('Dress')
        verbose_name_plural = _('Dresses')


class DressTranslation(ProductTranslation):
    product = models.ForeignKey(Dress, related_name='translations')


class DressVariant(ColoredVariant):
    product = models.ForeignKey(Dress, related_name='variants')
    SIZE_CHOICES = tuple([(str(s),str(s)) for s in range(8, 15)])
    size = models.CharField(choices=SIZE_CHOICES, max_length=2)

    def __unicode__(self):
        return '%s (%s / %s)' % (unicode(self.product), self.get_color_display(),
                                 self.get_size_display())


class Hat(Product):
    class Meta:
        verbose_name = _('Hat')
        verbose_name_plural = _('Hats')


class HatTranslation(ProductTranslation):
    product = models.ForeignKey(Hat, related_name='translations')


class HatVariant(satchless.product.models.Variant):
    product = models.ForeignKey(Hat, related_name='variants')

    def __unicode__(self):
        return unicode(self.product)


class Jacket(Product):
    class Meta:
        verbose_name = _('Jacket')
        verbose_name_plural = _('Jackets')


class JacketTranslation(ProductTranslation):
    product = models.ForeignKey(Jacket, related_name='translations')


class JacketVariant(ColoredVariant):
    product = models.ForeignKey(Jacket, related_name='variants')
    SIZE_CHOICES = tuple([(str(s),str(s)) for s in range(36, 49)])
    size = models.CharField(choices=SIZE_CHOICES, max_length=2)

    def __unicode__(self):
        return '%s (%s / %s)' % (unicode(self.product), self.get_color_display(),
                                 self.get_size_display())


class Shirt(Product):
    class Meta:
        verbose_name = _('Shirt')
        verbose_name_plural = _('Shirts')


class ShirtTranslation(ProductTranslation):
    product = models.ForeignKey(Shirt, related_name='translations')


class ShirtVariant(ColoredVariant):
    product = models.ForeignKey(Shirt, related_name='variants')
    SIZE_CHOICES = tuple([(str(s),str(s)) for s in range(8, 17)])
    size = models.CharField(choices=SIZE_CHOICES, max_length=2)

    def __unicode__(self):
        return '%s (%s / %s)' % (unicode(self.product), self.get_color_display(),
                                 self.get_size_display())


class TShirt(Product):
    class Meta:
        verbose_name = _('TShirt')
        verbose_name_plural = _('TShirts')


class TShirtTranslation(ProductTranslation):
    product = models.ForeignKey(TShirt, related_name='translations')


class TShirtVariant(ColoredVariant):
    product = models.ForeignKey(TShirt, related_name='variants')
    SIZE_CHOICES = (('S', 'S'), ('XS', 'XS'), ('M', 'M'), ('L', 'L'), ('XL', 'XL'))
    size = models.CharField(choices=SIZE_CHOICES, max_length=2)

    def __unicode__(self):
        return '%s / %s / %s' % (self.product, self.get_color_display(), self.get_size_display())


class Trousers(Product):
    class Meta:
        verbose_name = _('Trousers')
        verbose_name_plural = _('Trousers')


class TrousersTranslation(ProductTranslation):
    product = models.ForeignKey(Trousers, related_name='translations')


class TrousersVariant(ColoredVariant):
    product = models.ForeignKey(Trousers, related_name='variants')
    SIZE_CHOICES = tuple([(str(s),str(s)) for s in range(30, 39)])
    size = models.CharField(choices=SIZE_CHOICES, max_length=2)

    def __unicode__(self):
        return '%s / %s' % (self.get_color_display(), self.get_size_display())


def assign_main_image(sender, instance, **kwargs):
    if not kwargs.get('raw', False) and instance.product.main_image == None \
            and instance.product.images.exists():
        instance.product.main_image = instance.product.images.all()[0]
        instance.product.save()
models.signals.post_save.connect(assign_main_image, sender=ProductImage)

def assign_new_main_image(sender, instance, **kwargs):
    try:
        if instance.product.main_image == instance and instance.product.images.exists():
            instance.product.main_image = instance.product.images.all()[0]
            instance.product.save()
    except Product.DoesNotExist:
        pass
models.signals.post_delete.connect(assign_new_main_image, sender=ProductImage)

def _create_empty_hat_variant(sender, instance, created, **kwargs):
    if not kwargs.get('raw', False) and created:
        instance.variants.create()
models.signals.post_save.connect(_create_empty_hat_variant, sender=Hat)
