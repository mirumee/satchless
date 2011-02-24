# -*- coding:utf-8 -*-
from django.contrib import admin
from django.db.models.query import EmptyQuerySet
import django.db.models

import satchless.product.models
from satchless.product.admin import ProductAdmin, TranslationInline, CategoryAdmin, ProductForm

from . import models
from . import widgets

class ImageInline(admin.TabularInline):
    formfield_overrides = {
        django.db.models.ImageField: { 'widget': widgets.AdminImageWidget },
    }
    class Media:
        css = {
            'all': ['css/admin.css']
        }

class ProductWithImageForm(ProductForm):
    def __init__(self, *args, **kwargs):
        super(ProductWithImageForm, self).__init__(*args, **kwargs)
        if self.instance.id:
            self.fields['main_image'].queryset = models.ProductImage.objects.filter(product=self.instance)
        else:
            self.fields['main_image'].queryset = EmptyQuerySet(model=models.ProductImage)

class ProductWithImageAdmin(ProductAdmin):
    form = ProductWithImageForm

class ProductImageInline(ImageInline):
    model = models.ProductImage

class HatAdmin(ProductAdmin):
    pass

class TShirtVariantInline(admin.TabularInline):
    model = models.TShirtVariant

class TShirtAdmin(ProductAdmin):
    inlines = [ TShirtVariantInline, ProductImageInline ]

class ShirtVariantInline(admin.TabularInline):
    model = models.ShirtVariant

class ShirtAdmin(ProductWithImageAdmin):
    inlines = [ ShirtVariantInline, ProductImageInline ]

class CardiganVariantInline(admin.TabularInline):
    model = models.CardiganVariant

class CardiganAdmin(ProductWithImageAdmin):
    inlines = [ CardiganVariantInline, ProductImageInline ]

class JacketVariantInline(admin.TabularInline):
    model = models.JacketVariant

class JacketAdmin(ProductWithImageAdmin):
    inlines = [ JacketVariantInline, ProductImageInline ]

class TrousersVariantInline(admin.TabularInline):
    model = models.TrousersVariant

class TrousersAdmin(ProductWithImageAdmin):
    inlines = [ TrousersVariantInline, ProductImageInline ]

class DressVariantInline(admin.TabularInline):
    model = models.DressVariant

class DressAdmin(ProductWithImageAdmin):
    inlines = [ DressVariantInline, ProductImageInline ]

class CategoryImageInline(ImageInline):
    model = models.CategoryImage

class CategoryWithImageAdmin(CategoryAdmin):
   inlines = [ CategoryImageInline ]

admin.site.unregister(satchless.product.models.Category)
admin.site.register(satchless.product.models.Category, CategoryWithImageAdmin)

admin.site.register(models.Hat, HatAdmin)
admin.site.register(models.TShirt, TShirtAdmin)
admin.site.register(models.Shirt, ShirtAdmin)
admin.site.register(models.Cardigan, CardiganAdmin)
admin.site.register(models.Jacket, JacketAdmin)
admin.site.register(models.Trousers, TrousersAdmin)
admin.site.register(models.Dress, DressAdmin)
