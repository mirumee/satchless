# -*- coding:utf-8 -*-
from django.conf import settings
from django.contrib import admin
import django.db.models

from django.db.models.query import EmptyQuerySet

from satchless.contrib.pricing import simpleqty
import satchless.product.models
import satchless.product.admin
import satchless.category.models
import satchless.category.admin
import sale.models

from . import models
from . import widgets
from .forms import ProductPriceForm

class ImageInline(admin.TabularInline):
    formfield_overrides = {
        django.db.models.ImageField: { 'widget': widgets.AdminImageWidget },
    }

class ProductImageInline(ImageInline):
    extra = 4
    max_num = 4
    model = models.ProductImage
    sortable_field_name = "order"

class ProductForm(satchless.product.admin.ProductForm):
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        if self.instance.id:
            self.fields['main_image'].queryset =\
                (models.ProductImage.objects.filter(product=self.instance))
        else:
            self.fields['main_image'].queryset =\
                EmptyQuerySet(model=models.ProductImage)

class ProductAdmin(satchless.product.admin.ProductAdmin):
    form = ProductForm

class ProductImageInline(ImageInline):
    extra = 4
    man_num = 4
    model = models.ProductImage
    sortable_field_name = "order"

class PriceInline(admin.TabularInline):
    model = simpleqty.models.ProductPrice
    form = ProductPriceForm

class DiscountInline(admin.TabularInline):
    model = sale.models.DiscountGroup.products.through
    max_num = 1

class CategoryImageInline(ImageInline):
    model = models.CategoryImage

class CategoryWithImageAdmin(satchless.category.admin.CategoryAdmin):
    inlines = [CategoryImageInline]

class TacoVariantInline(admin.TabularInline):
    model = models.TacoVariant

class TacoAdmin(ProductAdmin):
    inlines = [ProductImageInline, TacoVariantInline, PriceInline,
            DiscountInline]

admin.site.unregister(satchless.category.models.Category)
admin.site.register(models.Category, CategoryWithImageAdmin)

admin.site.register(models.Taco, TacoAdmin)
