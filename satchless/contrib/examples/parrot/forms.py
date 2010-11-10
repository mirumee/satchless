from django import forms
from django.utils.translation import ugettext as _
from satchless.product.forms import BaseVariantForm
from . import models

class ParrotVariantForm(BaseVariantForm):
    color = forms.CharField(
            max_length=10,
            widget=forms.Select(choices=models.ParrotVariant.COLOR_CHOICES),
            label=_("Color"))
    looks_alive = forms.BooleanField(required=False, label=_("Looks alive"))

    def _get_variant_queryset(self):
        return models.ParrotVariant.objects.filter(
                product=self.product,
                color=self.cleaned_data['color'],
                looks_alive=self.cleaned_data.get('looks_alive', False))

    def clean(self):
        if not self._get_variant_queryset().exists():
            raise forms.ValidationError(_("Variant does not exist"))
        return self.cleaned_data

    def get_variant(self):
        return self._get_variant_queryset().get()
