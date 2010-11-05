from django import forms
from django.utils.translation import ugettext as _

from satchless.product.forms import BaseVariantForm

from . import models

class DummyVariantForm(BaseVariantForm):
    color = forms.CharField(label=_("color"), max_length=10,
            widget=forms.Select(choices=models.DummyVariant.COLOR_CHOICES))
    size = forms.IntegerField(label=_("size"), widget=forms.Select())

    def __init__(self, *args, **kwargs):
        super(DummyVariantForm, self).__init__(*args, **kwargs)
        sizes = self.product.variants.distinct().order_by('size').values_list('size')
        self.fields['size'].widget.choices = ((s[0],s[0]) for s in sizes)

    def _get_variant_queryset(self):
        return models.DummyVariant.objects.filter(
                product=self.product,
                color=self.cleaned_data['color'],
                size=self.cleaned_data['size'])

    def clean(self):
        if not self._get_variant_queryset().exists():
            raise forms.ValidationError, _("%(color)s variant of size %(size)s does not exist.") % \
                    self.cleaned_data
        return self.cleaned_data

    def get_variant(self):
        return self._get_variant_queryset().get()
