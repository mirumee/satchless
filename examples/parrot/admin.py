from django.contrib import admin
from satchless.product.admin import ProductAdmin, TranslationInline

from . import models

class ParrotVariantInline(admin.TabularInline):
    model = models.ParrotVariant

class ParrotTranslationInline(TranslationInline):
    model = models.ParrotTranslation

class ParrotAdmin(ProductAdmin):
    inlines = [ParrotTranslationInline, ParrotVariantInline]

admin.site.register(models.Parrot, ParrotAdmin)
