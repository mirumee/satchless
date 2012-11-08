# -*- coding:utf-8 -*-
import decimal
import operator
import os

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_images.models import Image
from django_prices.models import PriceField
from prices import Price, PriceModifier
from satchless.category.models import CategorizedProductMixin
from satchless.contrib.tax.flatgroups.models import TaxedProductMixin, TaxedVariantMixin
from satchless.contrib.stock.singlestore.models import VariantStockLevelMixin
import satchless.product.models
from satchless.util.models import construct

from categories.models import Category


class Discount(models.Model, PriceModifier):

    name = models.CharField(_('internal name'), max_length=100)
    rate = models.DecimalField(_('rate'), max_digits=4, decimal_places=2,
                               help_text=_('Percentile rate of the discount.'))
    rate_name = models.CharField(_('display name'), max_length=30,
                                 help_text=_(u'Name of the rate which will be '
                                             'displayed to the user.'))

    def apply(self, price):
        new_price = price - price * self.rate * decimal.Decimal('0.01')
        return Price(new_price.net, new_price.gross,
                     currency=new_price.currency,
                     previous=price, modifier=self, operation=operator.__add__)

    def __unicode__(self):
        return self.rate_name


class Product(TaxedProductMixin,
              construct(CategorizedProductMixin, category=Category),
              satchless.product.models.Product):

    QTY_MODE_CHOICES = (
        ('product', _("per product")),
        ('variant', _("per variant"))
    )
    qty_mode = models.CharField(_("Quantity pricing mode"), max_length=10,
                                choices=QTY_MODE_CHOICES, default='variant',
                                help_text=_("In 'per variant' mode the unit "
                                            "price will depend on quantity "
                                            "of single variant being sold. In "
                                            "'per product' mode, total "
                                            "quantity of all product's "
                                            "variants will be used."))
    price = PriceField(_("base price"), currency='EUR',
                       max_digits=12, decimal_places=4)
    discount = models.ForeignKey(Discount, null=True, blank=True,
                                 related_name='products')

    def __unicode__(self):
        return self.name

    def _get_base_price(self, quantity):
        overrides = self.qty_price_overrides.all()
        overrides = overrides.filter(min_qty__lte=quantity).order_by('-min_qty')
        try:
            return overrides[0].price
        except Exception:
            return self.price


class PriceQtyOverride(models.Model):
    """
    Overrides price of product unit, depending of total quantity being sold.
    """
    product = models.ForeignKey(Product, related_name='qty_price_overrides')
    min_qty = models.DecimalField(_("minimal quantity"), max_digits=10,
                                  decimal_places=4)
    price = PriceField(_("unit price"), currency='EUR',
                       max_digits=12, decimal_places=4)

    class Meta:
        ordering = ('min_qty',)


class Variant(TaxedVariantMixin, VariantStockLevelMixin,
              satchless.product.models.Variant):
    price_offset = PriceField(_("unit price offset"), currency='EUR',
                              default=0, max_digits=12, decimal_places=4)

    def get_price_per_item(self, discount=True, quantity=1, **kwargs):
        price = self.product._get_base_price(quantity=quantity)
        price += self.price_offset
        if discount and self.product.discount:
            price += self.product.discount
        return price


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


class Make(models.Model):
    name = models.TextField(_("manufacturer"), default='', blank=True)
    logo = models.ImageField(upload_to="make/logo/")

    def __unicode__(self):
        return self.name


class ProductBase(Product):
    name = models.CharField(_('name'), max_length=128)
    description = models.TextField(_('description'), blank=True)
    meta_description = models.TextField(_('meta description'), blank=True,
                                        help_text=_('Description used by search'
                                                    ' and indexing engines.'))
    make = models.ForeignKey(Make, null=True, blank=True,
                             on_delete=models.SET_NULL,
                             help_text=_("Product manufacturer"))
    main_image = models.ForeignKey(ProductImage, null=True, blank=True,
                                   on_delete=models.SET_NULL,
                                   help_text=_("Main product image"
                                               " (first image by default)"))

    class Meta:
        abstract = True


class ColoredVariant(Variant):
    COLOR_CHOICES = [
        ('red', _("Red")),
        ('green', _("Green")),
        ('blue', _("Blue"))]
    color = models.CharField(max_length=32, choices=COLOR_CHOICES)

    class Meta:
        abstract = True


class Cardigan(ProductBase):
    class Meta:
        verbose_name = _('Cardigan')
        verbose_name_plural = _('Cardigans')


class CardiganVariant(ColoredVariant):
    product = models.ForeignKey(Cardigan, related_name='variants')
    SIZE_CHOICES = [
        ('XS', 'XS'),
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL')]
    size = models.CharField(choices=SIZE_CHOICES, max_length=2)

    def __unicode__(self):
        return '%s (%s / %s)' % (self.product, self.get_color_display(),
                                 self.get_size_display())


class Dress(ProductBase):
    class Meta:
        verbose_name = _('Dress')
        verbose_name_plural = _('Dresses')


class DressVariant(ColoredVariant):
    product = models.ForeignKey(Dress, related_name='variants')
    SIZE_CHOICES = [(str(s), str(s)) for s in range(8, 15)]
    size = models.CharField(choices=SIZE_CHOICES, max_length=2)

    def __unicode__(self):
        return '%s (%s / %s)' % (unicode(self.product), self.get_color_display(),
                                 self.get_size_display())


class Hat(ProductBase):
    class Meta:
        verbose_name = _('Hat')
        verbose_name_plural = _('Hats')


class HatVariant(Variant):
    product = models.ForeignKey(Hat, related_name='variants')

    def __unicode__(self):
        return unicode(self.product)


class Jacket(ProductBase):
    class Meta:
        verbose_name = _('Jacket')
        verbose_name_plural = _('Jackets')


class JacketVariant(ColoredVariant):
    product = models.ForeignKey(Jacket, related_name='variants')
    SIZE_CHOICES = [(str(s), str(s)) for s in range(36, 49)]
    size = models.CharField(choices=SIZE_CHOICES, max_length=2)

    def __unicode__(self):
        return '%s (%s / %s)' % (unicode(self.product), self.get_color_display(),
                                 self.get_size_display())


class Shirt(ProductBase):
    class Meta:
        verbose_name = _('Shirt')
        verbose_name_plural = _('Shirts')


class ShirtVariant(ColoredVariant):
    product = models.ForeignKey(Shirt, related_name='variants')
    SIZE_CHOICES = [(str(s), str(s)) for s in range(8, 17)]
    size = models.CharField(choices=SIZE_CHOICES, max_length=2)

    def __unicode__(self):
        return '%s (%s / %s)' % (unicode(self.product), self.get_color_display(),
                                 self.get_size_display())


class TShirt(ProductBase):
    class Meta:
        verbose_name = _('TShirt')
        verbose_name_plural = _('TShirts')


class TShirtVariant(ColoredVariant):
    product = models.ForeignKey(TShirt, related_name='variants')
    SIZE_CHOICES = [
        ('XS', 'XS'),
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL')]
    size = models.CharField(choices=SIZE_CHOICES, max_length=2)

    def __unicode__(self):
        return u'%s / %s / %s' % (self.product, self.get_color_display(),
                                  self.get_size_display())


class Trousers(ProductBase):
    class Meta:
        verbose_name = _('Trousers')
        verbose_name_plural = _('Trousers')


class TrousersVariant(ColoredVariant):
    product = models.ForeignKey(Trousers, related_name='variants')
    SIZE_CHOICES = [(str(s), str(s)) for s in range(30, 39)]
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
        if (instance.product.main_image == instance and
                instance.product.images.exists()):
            instance.product.main_image = instance.product.images.all()[0]
            instance.product.save()
    except Product.DoesNotExist:
        pass
models.signals.post_delete.connect(assign_new_main_image, sender=ProductImage)
