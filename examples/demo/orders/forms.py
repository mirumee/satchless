import django.forms
import satchless.order.forms

from .app import order_app

class PaymentMethodForm(satchless.order.forms.PaymentMethodForm):

    class Meta:
        model = order_app.Order


class DeliveryMethodForm(satchless.order.forms.DeliveryMethodForm):

    class Meta:
        model = order_app.DeliveryGroup


class DeliveryDetailsForm(django.forms.ModelForm):

    class Meta:
        model = order_app.DeliveryGroup


class BillingForm(satchless.order.forms.BillingForm):

    class Meta:
        model = order_app.Order
        fields = ['billing_first_name', 'billing_last_name',
                  'billing_company_name', 'billing_street_address_1',
                  'billing_street_address_2', 'billing_city',
                  'billing_country_area', 'billing_postal_code',
                  'billing_country', 'billing_tax_id',
                  'billing_phone']
