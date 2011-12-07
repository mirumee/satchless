from django import forms
from django.utils.safestring import mark_safe

from ....delivery import models as delivery_models
from ....delivery import forms as delivery_forms

from .models import DeliveryCountry

class DeliveryVariantForm(forms.ModelForm):
    class Meta:
        model = delivery_models.DeliveryVariant
        exclude = ('delivery_group', 'name', 'description', 'price')


class PhysicalShippingDetailsForm(delivery_forms.PhysicalShippingDetailsForm):
    class Meta:
        model = delivery_models.PhysicalShippingDetails
        fields = ('shipping_first_name', 'shipping_last_name',
                  'shipping_company_name', 'shipping_street_address_1',
                  'shipping_street_address_2', 'shipping_city',
                  'shipping_country_area', 'shipping_postal_code',
                  'shipping_country', 'shipping_phone')

    def __init__(self, *args, **kwargs):
        super(PhysicalShippingDetailsForm, self).__init__(*args, **kwargs)
        self.fields['shipping_country'].choices = [(c.code, c.name) for c in DeliveryCountry.objects.deliverable()]