from django import forms
from django.contrib import admin

from . import models

class ProductSetItemInline(admin.TabularInline):
    model = models.ProductSetItem

class ProductSetAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    inlines = [
        ProductSetItemInline,
    ]

admin.site.register(models.ProductSet, ProductSetAdmin)
