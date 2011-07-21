from unidecode import unidecode
import urllib2
from django.utils.translation import ugettext as _
from satchless.delivery.models import DeliveryVariant, PhysicalShippingVariant
from satchless.payment import PaymentProvider, PaymentFailure
from authorizenet.utils import process_payment

from . import forms
from . import models

class AuthorizeNetProvider(PaymentProvider):
    unique_id = 'authorize.net'
    form_class = forms.PaymentForm

    def __init__(self, capture=True):
        self.capture = capture

    def enum_types(self, order=None, customer=None):
        return (('authorizenet', 'Authorize.net'),)

    def get_configuration_form(self, order, typ, data):
        instance = models.AuthorizeNetVariant(order=order, price=0)
        return self.form_class(data or None, instance=instance)

    def create_variant(self, order, typ, form):
        return form.save()

    def get_shipping_data(self, order):
        result = {}
        for dg in order.groups.all():
            try:
                shipping = dg.deliveryvariant.get_subtype_instance()
                if isinstance(shipping, PhysicalShippingVariant):
                    result['ship_to_first_name'] = shipping.shipping_first_name
                    result['ship_to_last_name'] = shipping.shipping_last_name
                    result['ship_to_company'] = shipping.shipping_company_name
                    address = filter(None,
                                     [shipping.shipping_street_address_1,
                                      shipping.shipping_street_address_2])
                    result['ship_to_address'] = '\n'.join(address)
                    result['ship_to_city'] = shipping.shipping_city
                    result['ship_to_state'] = shipping.shipping_country_area
                    result['ship_to_zip'] = shipping.shipping_postal_code
                    result['ship_to_country'] = shipping.get_shipping_country_display()
                    break
            except DeliveryVariant.DoesNotExist:
                pass
        return result

    def get_billing_data(self, order):
        result = {}
        result['first_name'] = order.billing_first_name
        result['last_name'] = order.billing_last_name
        result['company'] = order.billing_company_name
        address = filter(None,
                         [order.billing_street_address_1,
                          order.billing_street_address_2])
        result['address'] = '\n'.join(address)
        result['city'] = order.billing_city
        result['state'] = order.billing_country_area
        result['zip'] = order.billing_postal_code
        result['country'] = order.get_billing_country_display()
        result['phone'] = order.billing_phone
        if order.user:
            result['cust_id'] = str(order.user.pk)
            result['email'] = order.user.email
        return result

    def confirm(self, order):
        v = order.paymentvariant.get_subtype_instance()
        trans_type = self.capture and 'AUTH_CAPTURE' or 'AUTH_ONLY'
        data = {
            'card_num': v.cc_number,
            'exp_date': v.cc_expiration,
            'amount': order.total().gross,
            'invoice_num': order.pk,
            'type': trans_type,
        }
        if v.cc_cvv2:
            data['card_code'] = v.cc_cvv2
        data.update(self.get_billing_data(order))
        data.update(self.get_shipping_data(order))
        data = dict((k, unidecode(v) if isinstance(v, unicode) else v)
                    for k, v in data.items())
        try:
            response = process_payment(data, {})
        except urllib2.URLError:
            raise PaymentFailure(_("Could not connect to the gateway."))
        v.cc_cvv2 = ''  # Forget the CVV2 number immediately after the transaction
        v.response = response
        v.save()
        if not response.is_approved:
            raise PaymentFailure(response.response_reason_text)

class AuthorizeNetPreauthProvider(AuthorizeNetProvider):
    def __init__(self):
        return super(AuthorizeNetPreauthProvider, self).__init__(capture=False)
