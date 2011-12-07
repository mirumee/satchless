from django import forms

from ....delivery import models

class DeliveryVariantForm(forms.ModelForm):
    class Meta:
        model = models.DeliveryVariant
        exclude = ('delivery_group', 'name', 'description', 'price')
