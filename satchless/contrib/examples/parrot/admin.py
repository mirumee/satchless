from django.contrib import admin
from satchless.product.admin import ProductAdmin

from . import models

class ParrotVariantInline(admin.TabularInline):
    model = models.ParrotVariant

class ParrotAdmin(ProductAdmin):
    inlines = [ParrotVariantInline]

admin.site.register(models.Parrot, ParrotAdmin)
