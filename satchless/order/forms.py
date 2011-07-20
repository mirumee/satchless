from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import modelformset_factory
from django.utils.translation import ugettext as _

from . import handler
from . import models

class DeliveryMethodForm(forms.ModelForm):
    delivery_type = forms.ChoiceField(label=_('Delivery method'), choices=[])

    class Meta:
        model = models.DeliveryGroup
        fields = ('delivery_type',)

    def __init__(self, *args, **kwargs):
        super(DeliveryMethodForm, self).__init__(*args, **kwargs)
        types = handler.get_delivery_types(self.instance)
        self.fields['delivery_type'].choices = types

DeliveryMethodFormset = modelformset_factory(models.DeliveryGroup,
                                             form=DeliveryMethodForm, extra=0)

def get_delivery_details_forms_for_groups(groups, data):
    '''
    For each delivery group creates a (group, typ, delivery details form) tuple.
    If there is no form, the third element is None.
    '''
    groups_and_forms = []
    for group in groups:
        delivery_type = group.delivery_type
        form = None
        form = handler.get_delivery_form(group, data)
        groups_and_forms.append((group, delivery_type, form))
    return groups_and_forms


class PaymentMethodForm(forms.ModelForm):
    payment_type = forms.ChoiceField(choices=())
    class Meta:
        model = models.Order
        fields = ('payment_type',)

    def __init__(self, *args, **kwargs):
        super(PaymentMethodForm, self).__init__(*args, **kwargs)
        types = handler.get_payment_types(self.instance)
        self.fields['payment_type'].choices = types

def get_payment_details_form(order, data):
    return handler.get_payment_form(order, data)

class BillingForm(forms.ModelForm):
    REQUIRED_FIELDS = (
        'billing_first_name', 'billing_last_name',
        'billing_street_address_1', 'billing_city', 'billing_country_area',
        'billing_country', 'billing_postal_code', 'billing_country',
        'billing_phone'
    )

    class Meta:
        model = models.Order
        fields = ('billing_first_name', 'billing_last_name',
                  'billing_company_name', 'billing_street_address_1',
                  'billing_street_address_2', 'billing_city',
                  'billing_country_area', 'billing_country',
                  'billing_postal_code', 'billing_country', 'billing_tax_id',
                  'billing_phone')

    def __init__(self, *args, **kwargs):
        super(BillingForm, self).__init__(*args, **kwargs)
        for f in self.REQUIRED_FIELDS:
            self.fields[f].required = True
