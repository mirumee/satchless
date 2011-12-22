from django import forms
from django.utils.translation import ugettext_lazy as _

from . import handler

class DeliveryMethodForm(forms.ModelForm):
    delivery_type = forms.ChoiceField(label=_('Delivery method'), choices=[])

    class Meta:
        fields = ('delivery_type',)

    def __init__(self, *args, **kwargs):
        super(DeliveryMethodForm, self).__init__(*args, **kwargs)
        types = handler.delivery_queue.as_choices(delivery_group=self.instance)
        self.fields['delivery_type'].choices = types


def get_delivery_details_forms_for_groups(groups, data):
    '''
    For each delivery group creates a (group, typ, delivery details form) tuple.
    If there is no form, the third element is None.
    '''
    groups_and_forms = []
    for group in groups:
        delivery_type = group.delivery_type
        form = handler.delivery_queue.get_configuration_form(group, data)
        groups_and_forms.append((group, delivery_type, form))
    return groups_and_forms


class PaymentMethodForm(forms.ModelForm):
    payment_type = forms.ChoiceField(choices=())

    class Meta:
        fields = ('payment_type',)

    def __init__(self, *args, **kwargs):
        super(PaymentMethodForm, self).__init__(*args, **kwargs)
        types = get_payment_choices(self.instance)
        self.fields['payment_type'].choices = types


def get_payment_choices(order):
    return list(handler.payment_queue.as_choices(order=order))

def get_payment_type_display(order, value):
    '''
    Note:
    Probably returns a django.utils.functional.__proxy__ object (lazy translation)
    If you're not using it in a template (eg saving to db) then wrap the
    returned value in unicode() to evaluate it.
    '''
    return next((x[1] for x in get_payment_choices(order) if x[0] == value), None)

def get_payment_details_form(order, data):
    return handler.payment_queue.get_configuration_form(order, data)


class ShippingForm(forms.ModelForm):
    class Meta:
        fields = ['shipping_first_name', 'shipping_last_name',
                  'shipping_company_name', 'shipping_street_address_1',
                  'shipping_street_address_2', 'shipping_city',
                  'shipping_postal_code', 'shipping_country',
                  'shipping_country_area', 'shipping_phone']


class BillingForm(forms.ModelForm):
    class Meta:
        fields = ['billing_first_name', 'billing_last_name',
                  'billing_company_name', 'billing_street_address_1',
                  'billing_street_address_2', 'billing_city',
                  'billing_country_area', 'billing_postal_code',
                  'billing_country', 'billing_tax_id',
                  'billing_phone']

