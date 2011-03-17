# -*- coding:utf-8 -*-
from django.contrib import admin
from django.db.models.query import EmptyQuerySet
import django.db.models

from satchless.contrib.pricing import simpleqty
import satchless.product.models
import satchless.product.admin
import sale.models

from . import models
from . import widgets

class ImageInline(admin.TabularInline):
    formfield_overrides = {
        django.db.models.ImageField: { 'widget': widgets.AdminImageWidget },
    }

class ProductForm(satchless.product.admin.ProductForm):
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        if self.instance.id:
            self.fields['main_image'].queryset = models.ProductImage.objects.filter(product=self.instance)
        else:
            self.fields['main_image'].queryset = EmptyQuerySet(model=models.ProductImage)

class ProductAdmin(satchless.product.admin.ProductAdmin):
    form = ProductForm

class ProductImageInline(ImageInline):
    extra = 4
    max_num = 4
    model = models.ProductImage
    sortable_field_name = "order"

class PriceInline(admin.TabularInline):
    model = simpleqty.models.ProductPrice

class DiscountInline(admin.TabularInline):
    model = sale.models.DiscountGroup.products.through
    max_num = 1

class CardiganVariantInline(admin.TabularInline):
    model = models.CardiganVariant

class CardiganTranslationInline(satchless.product.admin.TranslationInline):
    model = models.CardiganTranslation

class CardiganAdmin(ProductAdmin):
    inlines = [ CardiganTranslationInline, CardiganVariantInline, ProductImageInline ]

class DressVariantInline(admin.TabularInline):
    model = models.DressVariant

class DressTranslationInline(satchless.product.admin.TranslationInline):
    model = models.DressTranslation

class DressAdmin(ProductAdmin):
    inlines = [ DressTranslationInline, PriceInline, DiscountInline, DressVariantInline, ProductImageInline ]

class HatTranslationInline(satchless.product.admin.TranslationInline):
    model = models.HatTranslation

class HatAdmin(ProductAdmin):
    inlines = [ HatTranslationInline, PriceInline, DiscountInline, ProductImageInline ]

class JacketVariantInline(admin.TabularInline):
    model = models.JacketVariant

class JacketTranslationInline(satchless.product.admin.TranslationInline):
    model = models.JacketTranslation

class JacketAdmin(ProductAdmin):
    inlines = [ JacketTranslationInline, PriceInline, DiscountInline, JacketVariantInline, ProductImageInline ]

class ShirtVariantInline(admin.TabularInline):
    model = models.ShirtVariant

class ShirtTranslationInline(satchless.product.admin.TranslationInline):
    model = models.ShirtTranslation

class ShirtAdmin(ProductAdmin):
    inlines = [ ShirtTranslationInline, ShirtVariantInline, ProductImageInline ]

class TrousersVariantInline(admin.TabularInline):
    model = models.TrousersVariant

class TrousersTranslationInline(satchless.product.admin.TranslationInline):
    model = models.TrousersTranslation

class TrousersAdmin(ProductAdmin):
    inlines = [ TrousersTranslationInline, TrousersVariantInline, ProductImageInline ]

class TShirtVariantInline(admin.TabularInline):
    model = models.TShirtVariant

class TShirtTranslationInline(satchless.product.admin.TranslationInline):
    model = models.TShirtTranslation

class TShirtAdmin(ProductAdmin):
    inlines = [ TShirtTranslationInline, TShirtVariantInline, ProductImageInline ]

class CategoryImageInline(ImageInline):
    model = models.CategoryImage

class CategoryTranslationInline(satchless.product.admin.TranslationInline):
    model = satchless.product.models.CategoryTranslation

class CategoryWithImageAdmin(satchless.product.admin.CategoryAdmin):
   inlines = [ CategoryTranslationInline, CategoryImageInline ]

admin.site.register(models.Cardigan, CardiganAdmin)
admin.site.register(models.Dress, DressAdmin)
admin.site.register(models.Hat, HatAdmin)
admin.site.register(models.Jacket, JacketAdmin)
admin.site.register(models.Shirt, ShirtAdmin)
admin.site.register(models.Trousers, TrousersAdmin)
admin.site.register(models.TShirt, TShirtAdmin)

admin.site.unregister(satchless.product.models.Category)
admin.site.register(satchless.product.models.Category, CategoryWithImageAdmin)
