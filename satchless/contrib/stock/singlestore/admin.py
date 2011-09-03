from django.contrib import admin
from django.forms.models import BaseInlineFormSet
from django import forms

from satchless.forms.widgets import DecimalInput
from . import models

class VariantStockLevelFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super(VariantStockLevelFormSet, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            variants = self.instance.get_subtype_instance().variants.all()
            for form in self.forms:
                form.fields['variant'].queryset = variants

class VariantStockLevelForm(forms.ModelForm):
    class Meta:
        widgets = {
            'quantity': DecimalInput(),
        }


class VariantStockLevelInline(admin.TabularInline):
    model = models.StockLevel
    form = VariantStockLevelForm
    formset = VariantStockLevelFormSet

admin.site.register(models.StockLevel)
