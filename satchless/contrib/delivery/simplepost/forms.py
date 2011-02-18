from django import forms

from . import models

class PostShippingVariantForm(forms.ModelForm):
    class Meta:
        model = models.PostShippingVariant
