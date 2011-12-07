from django import forms
from django.forms.models import modelformset_factory

from . import models

class PhysicalShippingDetailsForm(forms.ModelForm):
    REQUIRED_FIELDS = (
        'shipping_first_name', 'shipping_last_name',
        'shipping_street_address_1', 'shipping_city', 'shipping_country_area',
        'shipping_country', 'shipping_postal_code', 'shipping_phone'
    )

    class Meta:
        model = models.PhysicalShippingDetails
        fields = ('shipping_first_name', 'shipping_last_name',
                  'shipping_company_name', 'shipping_street_address_1',
                  'shipping_street_address_2', 'shipping_city',
                  'shipping_country_area', 'shipping_postal_code',
                  'shipping_country', 'shipping_phone')

    def __init__(self, *args, **kwargs):
        super(PhysicalShippingDetailsForm, self).__init__(*args, **kwargs)
        for f in self.REQUIRED_FIELDS:
            self.fields[f].required = True

PhysicalShippingFormset = modelformset_factory(models.PhysicalShippingDetails,
                                               form=PhysicalShippingDetailsForm, extra=0)
