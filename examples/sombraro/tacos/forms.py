from django import forms
from satchless.forms.widgets import DecimalInput
from satchless.product.forms import BaseVariantForm
from models import Taco, TacoVariant

class ProductPriceForm(forms.ModelForm):
    class Meta:
        widgets = {
            'price': DecimalInput(min_decimal_places=2),
        }

class TacoVariantForm(BaseVariantForm):
    size = forms.CharField(
            max_length=6,
            widget=forms.Select(choices=[]))

    def __init__(self, *args, **kwargs):
        super(TacoVariantForm, self).__init__(*args, **kwargs)
        used_sizes = self.product.variants.values_list('size', flat=True).distinct()
        size_choices = [(k, v)
                        for k, v in TacoVariant.SIZE_CHOICES
                        if k in used_sizes]
        self.fields['size'].widget.choices = size_choices

    def _get_variant_queryset(self):
        return TacoVariant.objects.filter(
            product=self.product,
            size=self.cleaned_data['size'],
        )

    def clean(self):
        if not self._get_variant_queryset().exists():
            raise forms.ValidationError("We are sorry but we don't carry this"
                                        "size of taco")
        return self.cleaned_data

    def get_variant(self):
        return self._get_variant_queryset().get()
