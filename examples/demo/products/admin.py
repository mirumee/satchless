# -*- coding:utf-8 -*-
from django.conf import settings
from django.contrib import admin
import django.db.models
from django.db.models.query import EmptyQuerySet

import satchless.category.admin
import satchless.contrib.pricing.simpleqty.admin
import satchless.product.models
import satchless.product.admin
import sale.models

from . import models
from . import widgets

class TranslationInline(admin.StackedInline):
    extra = 1
    max_num = len(settings.LANGUAGES) - 1


class ImageInline(admin.TabularInline):
    formfield_overrides = {
        django.db.models.ImageField: { 'widget': widgets.AdminImageWidget },
    }


class ProductForm(satchless.category.admin.ProductForm):
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        if self.instance.id:
            self.fields['main_image'].queryset = (models.ProductImage.objects
                                                        .filter(product=self.instance))
        else:
            self.fields['main_image'].queryset = EmptyQuerySet(model=models.ProductImage)


class ProductAdmin(satchless.category.admin.ProductAdmin):
    form = ProductForm


class ProductImageInline(ImageInline):
    extra = 4
    max_num = 4
    model = models.ProductImage
    sortable_field_name = "order"


class PriceInline(admin.TabularInline):
    model = satchless.contrib.pricing.simpleqty.models.ProductPrice
    form = satchless.contrib.pricing.simpleqty.admin.ProductPriceForm


class DiscountInline(admin.TabularInline):
    model = sale.models.DiscountGroup.products.through
    max_num = 1


class CardiganVariantInline(admin.TabularInline):
    model = models.CardiganVariant


class CardiganTranslationInline(TranslationInline):
    model = models.CardiganTranslation


class CardiganAdmin(ProductAdmin):
    inlines = [CardiganTranslationInline, CardiganVariantInline, ProductImageInline]


class DressVariantInline(admin.TabularInline):
    model = models.DressVariant


class DressTranslationInline(TranslationInline):
    model = models.DressTranslation


class DressAdmin(ProductAdmin):
    inlines = [DressTranslationInline, DressVariantInline, PriceInline,
               DiscountInline, ProductImageInline]


class HatTranslationInline(TranslationInline):
    model = models.HatTranslation


class HatAdmin(ProductAdmin):
    inlines = [HatTranslationInline, PriceInline, DiscountInline,
               ProductImageInline]


class JacketVariantInline(admin.TabularInline):
    model = models.JacketVariant


class JacketTranslationInline(TranslationInline):
    model = models.JacketTranslation


class JacketAdmin(ProductAdmin):
    inlines = [JacketTranslationInline, PriceInline, DiscountInline,
               JacketVariantInline, ProductImageInline]


class ShirtVariantInline(admin.TabularInline):
    model = models.ShirtVariant


class ShirtTranslationInline(TranslationInline):
    model = models.ShirtTranslation


class ShirtAdmin(ProductAdmin):
    inlines = [ShirtTranslationInline, ShirtVariantInline,
               PriceInline, DiscountInline, ProductImageInline]


class TrousersVariantInline(admin.TabularInline):
    model = models.TrousersVariant


class TrousersTranslationInline(TranslationInline):
    model = models.TrousersTranslation


class TrousersAdmin(ProductAdmin):
    inlines = [TrousersTranslationInline, TrousersVariantInline,
               PriceInline, DiscountInline, ProductImageInline]


class TShirtVariantInline(admin.TabularInline):
    model = models.TShirtVariant


class TShirtTranslationInline(TranslationInline):
    model = models.TShirtTranslation


class TShirtAdmin(ProductAdmin):
    inlines = [TShirtTranslationInline, TShirtVariantInline,
               PriceInline, DiscountInline, ProductImageInline]


admin.site.register(models.Cardigan, CardiganAdmin)
admin.site.register(models.Dress, DressAdmin)
admin.site.register(models.Hat, HatAdmin)
admin.site.register(models.Jacket, JacketAdmin)
admin.site.register(models.Shirt, ShirtAdmin)
admin.site.register(models.Trousers, TrousersAdmin)
admin.site.register(models.TShirt, TShirtAdmin)

admin.site.register(models.Make)
