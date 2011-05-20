from django import forms

from . import models

class PostShippingVariantForm(forms.ModelForm):
    class Meta:
        model = models.PostShippingVariant
        fields = ('shipping_first_name', 'shipping_last_name',
                  'shipping_company_name', 'shipping_street_address_1',
                  'shipping_street_address_2', 'shipping_city',
                  'shipping_postal_code', 'shipping_country', 'shipping_phone')
