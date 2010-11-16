from django.forms.models import BaseInlineFormSet
from django.contrib import admin
from . import models

class VariantOffsetFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super(VariantOffsetFormSet, self).__init__(*args, **kwargs)
        if self.instance:
            variants = self.instance.product.get_subtype_instance().variants.all()
            for form in self.forms:
                form.fields['variant'].queryset = variants

class PriceQtyOverrideInline(admin.TabularInline):
    model = models.PriceQtyOverride

class VariantPriceOffsetInline(admin.TabularInline):
    model = models.VariantPriceOffset
    formset = VariantOffsetFormSet

class ProductPriceAdmin(admin.ModelAdmin):
    inlines = [PriceQtyOverrideInline, VariantPriceOffsetInline]

admin.site.register(models.ProductPrice, ProductPriceAdmin)
