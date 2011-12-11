# -*- coding:utf-8 -*-
from django.contrib import admin

from products.admin import ImageInline, TranslationInline
import satchless.category.models

from . import models

class CategoryTranslationInline(TranslationInline):
    model = models.CategoryTranslation

class CategoryImageInline(ImageInline):
    model = models.CategoryImage


class CategoryTranslationInline(TranslationInline):
    model = models.CategoryTranslation


class CategoryWithImageAdmin(satchless.category.admin.CategoryAdmin):
   inlines = [CategoryTranslationInline, CategoryImageInline]

admin.site.unregister(satchless.category.models.Category)
admin.site.register(models.Category, CategoryWithImageAdmin)
