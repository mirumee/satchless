from ConfigParser import ConfigParser
from decimal import Decimal
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from io import StringIO
from suds.client import Client as SudsClient
import calendar
import datetime
import os

from ....payment import PaymentProvider, PaymentFailure, PaymentType
from . import forms
from . import models

class PaymentsGatewayProvider(PaymentProvider):
    form_class = forms.PaymentForm

    def enum_types(self, order=None, customer=None):
        yield self, PaymentType(typ='paymentsgateway',
                                name='paymentsgateway.com')

    def get_configuration_form(self, order, typ, data):
        instance = models.PaymentsGatewayVariant(order=order, price=0)
        return self.form_class(data or None, instance=instance)

    def create_variant(self, order, form, typ=None):
        if form.is_valid():
            return form.save()
        raise PaymentFailure(_("Could not create PaymentsGateway Variant"))

    def confirm(self, order, typ=None, variant=None):
        if not variant:
            variant = order.paymentvariant
        v = variant.get_subtype_instance()
        amount = str(v.amount.quantize(Decimal('.01')))

        svc = SudsClient(settings.PG_PAYMENT_WSDL).service
        kwargs = {
            'pg_merchant_id': settings.PG_MERCHANT_ID,
            'pg_password': settings.PG_TRANSACTION_PASSWORD,
            'pg_transaction_type': "10", # CC sale
            'pg_total_amount': amount,
        }

        if v.pg_payment_token:
            result = \
                svc.ExecuteSocketQuery(pg_payment_method_id=v.pg_payment_token,
                                       **kwargs)
        elif v.pg_client_token:
            result = \
                svc.ExecuteSocketQuery(pg_client_id=v.pg_client_token,
                                       **kwargs)
        else:
            raise PaymentFailure(_("Requires a payment method or client."))

        data = {}
        try:
            # make a fake ini file so we can parse with ConfigParser
            data_string = str(result)
            data_string = data_string[0:data_string.find('endofdata')]
            properties = StringIO()
            properties.write(u'[rootsection]\n')
            properties.write(unicode(data_string))
            properties.seek(0, os.SEEK_SET)
            cp = ConfigParser()
            cp.readfp(properties)
            data = vars(cp).get('_sections').get('rootsection')
        except Exception as e:
            # whatever happened, keep going, for logging purposes.
            data['other_error'] = str(e)
        finally:
            receipt_form = forms.PaymentsGatewayReceiptForm(data)
            if receipt_form.is_valid():
                v.receipt = receipt_form.save()
                v.name = ""
                v.description = ""
                v.save()
            if not data.get('pg_response_type') or \
                data.get('pg_response_type') != 'A':
                raise PaymentFailure("%s %s" %
                     (data.get('pg_response_code'),
                      data.get('pg_response_description')))
