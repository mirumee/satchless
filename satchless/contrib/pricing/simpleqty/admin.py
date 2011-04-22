from django import forms
from django.forms.models import BaseInlineFormSet
from django.contrib import admin

from satchless.forms.widgets import DecimalInput
from . import models

class PriceQtyOverrideForm(forms.ModelForm):
    class Meta:
        widgets = {
            'min_qty': DecimalInput(),
            'price': DecimalInput(min_decimal_places=2),
        }


class PriceQtyOverrideInline(admin.TabularInline):
    model = models.PriceQtyOverride
    form = PriceQtyOverrideForm


class VariantOffsetForm(forms.ModelForm):
    class Meta:
        widgets = {
            'price_offset': DecimalInput(min_decimal_places=2),
        }


class VariantOffsetFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super(VariantOffsetFormSet, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            variants = self.instance.product.get_subtype_instance().variants.all()
            for form in self.forms:
                form.fields['variant'].queryset = variants


class VariantPriceOffsetInline(admin.TabularInline):
    model = models.VariantPriceOffset
    form = VariantOffsetForm
    formset = VariantOffsetFormSet

class ProductPriceForm(forms.ModelForm):
    class Meta:
        widgets = {
            'price': DecimalInput(min_decimal_places=2),
        }

class ProductPriceAdmin(admin.ModelAdmin):
    inlines = [PriceQtyOverrideInline, VariantPriceOffsetInline]
    form = ProductPriceForm

admin.site.register(models.ProductPrice, ProductPriceAdmin)
