from django.contrib import admin
from satchless.product.admin import ProductAdmin

from . import models

class DummyVariantInline(admin.TabularInline):
    model = models.DummyVariant

class DummyAdmin(ProductAdmin):
    inlines = [DummyVariantInline]

admin.site.register(models.Dummy, DummyAdmin)
