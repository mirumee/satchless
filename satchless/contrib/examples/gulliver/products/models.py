# -*- coding:utf-8 -*-
import os

from django.db import models
from django.utils.translation import ugettext as _
from django.db.models import permalink

from satchless.product.models import ( Product, ProductAbstract,
        Variant, ProductAbstractTranslation, Category )
from satchless.image.models import Image

class CategoryImage(Image):
    category = models.OneToOneField(Category, related_name='image')
    class Meta:
        verbose_name_plural = _("Category image")

class ProductImage(Image):
    product = models.ForeignKey(Product, related_name="images")
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

class ProductWithImage(ProductAbstract):
    manufacture = models.TextField(_("Manufacture"), default='', blank=True)
    main_image = models.ForeignKey(ProductImage, null=True, blank=True, on_delete=models.SET_NULL,
            help_text=_("Main product image (first image by default)"))

    class Meta:
        abstract = True

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

class ColoredVariant(Variant):
    COLOR_CHOICES = (('red', _("red")), ('green', _("green")), ('blue', _("blue")))
    color = models.CharField(max_length=32, choices=COLOR_CHOICES)
    class Meta:
        abstract = True

class TShirt(ProductWithImage):
    pass

class TShirtVariant(ColoredVariant):
    product = models.ForeignKey(TShirt, related_name='variants')
    SIZE_CHOICES = (('S', 'S'), ('XS', 'XS'), ('M', 'M'), ('L', 'L'), ('XL', 'XL'))
    size = models.CharField(choices=SIZE_CHOICES, max_length=2)

class Hat(ProductWithImage):
    pass

class Hat(Variant):
    product = models.ForeignKey(TShirt, related_name='variants')

class Shirt(ProductWithImage):
    pass

class ShirtVariant(ColoredVariant):
    product = models.ForeignKey(Shirt, related_name='variants')
    SIZE_CHOICES = tuple([(str(s),str(s)) for s in range(8, 17)])
    size = models.CharField(choices=SIZE_CHOICES, max_length=2)

    def __unicode__(self):
        return '%s / %s' % (self.get_color_display(), self.get_size_display())

class Cardigan(ProductWithImage):
    pass

class CardiganVariant(ColoredVariant):
    product = models.ForeignKey(Cardigan, related_name='variants')
    SIZE_CHOICES = (('S', 'S'), ('XS', 'XS'), ('M', 'M'), ('L', 'L'), ('XL', 'XL'))
    size = models.CharField(choices=SIZE_CHOICES, max_length=2)

    def __unicode__(self):
        return '%s / %s' % (self.get_color_display(), self.get_size_display())

class Jacket(ProductWithImage):
    pass

class JacketVariant(ColoredVariant):
    product = models.ForeignKey(Jacket, related_name='variants')
    SIZE_CHOICES = tuple([(str(s),str(s)) for s in range(36, 49)])
    size = models.CharField(choices=SIZE_CHOICES, max_length=2)

    def __unicode__(self):
        return '%s / %s' % (self.get_color_display(), self.get_size_display())

class Trousers(ProductWithImage):
    pass

class TrousersVariant(ColoredVariant):
    product = models.ForeignKey(Trousers, related_name='variants')
    SIZE_CHOICES = tuple([(str(s),str(s)) for s in range(30, 39)])
    size = models.CharField(choices=SIZE_CHOICES, max_length=2)

    def __unicode__(self):
        return '%s / %s' % (self.get_color_display(), self.get_size_display())

class Dress(ProductWithImage):
    pass

class DressVariant(ColoredVariant):
    product = models.ForeignKey(Dress, related_name='variants')
    SIZE_CHOICES = tuple([(str(s),str(s)) for s in range(8, 15)])
    size = models.CharField(choices=SIZE_CHOICES, max_length=2)

    def __unicode__(self):
        return '%s / %s' % (self.get_color_display(), self.get_size_display())
