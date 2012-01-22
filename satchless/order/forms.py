from django import forms
from django.forms.models import BaseModelFormSet
from django.utils.translation import ugettext_lazy as _


class DeliveryMethodForm(forms.ModelForm):

    delivery_type = forms.ChoiceField(label=_('Delivery method'), choices=[])

    class Meta:
        fields = ('delivery_type',)

    def __init__(self, delivery_queue, *args, **kwargs):
        super(DeliveryMethodForm, self).__init__(*args, **kwargs)
        types = delivery_queue.as_choices(delivery_group=self.instance)
        self.fields['delivery_type'].choices = types


class DeliveryMethodFormSet(BaseModelFormSet):

    def __init__(self, delivery_queue, *args, **kwargs):
        self.delivery_queue = delivery_queue
        super(DeliveryMethodFormSet, self).__init__(*args, **kwargs)

    def _construct_form(self, *args, **kwargs):
        kwargs['delivery_queue'] = self.delivery_queue
        return super(DeliveryMethodFormSet, self)._construct_form(*args, **kwargs)


class PaymentMethodForm(forms.ModelForm):

    payment_type = forms.ChoiceField(choices=[])

    class Meta:
        fields = ('payment_type',)

    def __init__(self, payment_queue, *args, **kwargs):
        super(PaymentMethodForm, self).__init__(*args, **kwargs)
        types = payment_queue.as_choices(order=self.instance)
        self.fields['payment_type'].choices = types


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

