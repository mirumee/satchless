from django import forms
from satchless.product.forms import BaseVariantForm
from . import models

class ParrotVariantForm(BaseVariantForm):
    color = forms.CharField(
            max_length=10,
            widget=forms.Select(choices=models.ParrotVariant.COLOR_CHOICES))
    looks_alive = forms.BooleanField(required=False)

    def _get_variant_queryset(self):
        return models.ParrotVariant.objects.filter(
                product=self.product,
                color=self.cleaned_data['color'],
                looks_alive=self.cleaned_data.get('looks_alive', False))

    def clean(self):
        if not self._get_variant_queryset().exists():
            raise forms.ValidationError("Variant does not exist")
        return self.cleaned_data

    def get_variant(self):
        return self._get_variant_queryset().get()
