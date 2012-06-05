from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from suds.client import Client as SudsClient
import calendar

from ....payment import PaymentProvider, PaymentFailure, PaymentType
from . import forms
from . import models

import datetime
from io import StringIO
import os
from ConfigParser import ConfigParser

class PaymentsGatewayProvider(PaymentProvider):
    form_class = forms.PaymentForm

    def enum_types(self, order=None, customer=None):
        yield self, PaymentType(typ='paymentsgateway', name='paymentsgateway.com')

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
        amount = str(v.amount)

        pay_client = SudsClient(settings.PG_PAYMENT_WSDL)
        service = pay_client.service
        if v.pg_payment_token:
            result = service.ExecuteSocketQuery(pg_merchant_id=settings.PG_MERCHANT_ID,
                                                pg_password=settings.PG_TRANSACTION_PASSWORD,
                                                pg_transaction_type="10", # CC sale
                                                pg_total_amount=amount,
                                                pg_payment_method_id=v.pg_payment_token)
        elif v.pg_client_token:
            result = service.ExecuteSocketQuery(pg_merchant_id=settings.PG_MERCHANT_ID,
                                                pg_password=settings.PG_TRANSACTION_PASSWORD,
                                                pg_transaction_type="10", # CC sale
                                                pg_total_amount=amount,
                                                pg_client_id=v.pg_client_token)
        else:
            raise PaymentFailure(_("Requires either a payment method or client."))

        data = {}
        try:
            config = StringIO()
            config.write('[rootsection]')
            data_string = str(result).replace('endofdata', '')
            config.write(data_string)
            config.seek(0, os.SEEK_SET)
            cp = ConfigParser()
            cp.readfp(config)
            data = vars(cp).get('_sections').get('rootsection')
        except Exception:
            pass
        finally:
            receipt_form = forms.PaymentsGatewayReceiptForm(data)
            if receipt_form.is_valid():
                v.receipt = receipt_form.save()
                v.name = ""
                v.description = ""
                v.save()
