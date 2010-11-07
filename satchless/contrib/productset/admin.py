from django import forms
from django.contrib import admin

from . import models

class ProductSetItemInline(admin.TabularInline):
    model = models.ProductSetItem

class ProductSetImageInline(admin.TabularInline):
    model = models.ProductSetImage

class ProductSetAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    inlines = [
        ProductSetItemInline,
        ProductSetImageInline,
    ]

admin.site.register(models.ProductSet, ProductSetAdmin)
