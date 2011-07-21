from django import forms
from django.utils.translation import ugettext as _
from . import models

class AddressForm(forms.ModelForm):
    class Meta:
        model = models.Address
        exclude = ('customer',)

class AddressFormWithDefaultCheckboxes(AddressForm):
    set_as_default_billing = forms.BooleanField(label=_("Set as default billing"), required=False)
    set_as_default_shipping = forms.BooleanField(label=_("Set as default shipping"), required=False)

    def __init__(self, *args, **kwargs):
        super(AddressFormWithDefaultCheckboxes, self).__init__(*args, **kwargs)
        try:
            customer = self.instance.customer
            self.fields['set_as_default_billing'].initial = \
                    customer.billing_address == self.instance
            self.fields['set_as_default_shipping'].initial = \
                    customer.shipping_address == self.instance
        except models.Customer.DoesNotExist:
            pass

    def save(self, *args, **kwargs):
        super(AddressFormWithDefaultCheckboxes, self).save(*args, **kwargs)
        if self.cleaned_data['set_as_default_billing']:
            self.instance.customer.billing_address = self.instance
        if self.cleaned_data['set_as_default_shipping']:
            self.instance.customer.shipping_address = self.instance
        self.instance.customer.save()
        return self.instance
