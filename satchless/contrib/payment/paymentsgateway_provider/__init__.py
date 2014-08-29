from ConfigParser import ConfigParser
from decimal import Decimal
from django.conf import settings
from django.db.models.query_utils import Q
from django.utils.translation import ugettext_lazy as _
from io import StringIO
from suds.client import Client as SudsClient
import datetime
import os

from ....payment import PaymentProvider, PaymentFailure, PaymentType
from . import forms
from . import models
import string
import random


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

def pg_pay(variant, transaction_type, amount=None, first_name=None,
           last_name=None, client_token=None, payment_token=None,
           merchant_data=None, dict_extras=None):
    svc = SudsClient(settings.PG_PAYMENT_WSDL).service
    kwargs = {
        'pg_merchant_id': settings.PG_MERCHANT_ID,
        'pg_password': settings.PG_TRANSACTION_PASSWORD,
        'pg_transaction_type': transaction_type,
    }
    if amount:
        kwargs['pg_total_amount'] = amount
    if first_name:
        kwargs['ecom_billto_postal_name_first'] = first_name
    if last_name:
        kwargs['ecom_billto_postal_name_last'] = last_name
    if client_token:
        kwargs['pg_client_id'] = client_token
    if payment_token:
        kwargs['pg_payment_method_id'] = payment_token
    if merchant_data:
        kwargs['pg_merchant_data_1'] = merchant_data
    if dict_extras:
        kwargs.update(dict_extras)

    result = svc.ExecuteSocketQuery(**kwargs)

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
            variant.receipt = receipt_form.save()
            variant.name = "Credit"
            variant.description = ""
            variant.save()
        if data.get('pg_response_type') != 'A':
            raise PaymentFailure("%s %s" %
                                 (data.get('pg_response_code'),
                                  data.get('pg_response_description')))

def auth_via_cc(variant, amount, first_name=None, last_name=None,
                client_token=None, payment_token=None):
    random_order_id = { 'ecom_consumerorderid': id_generator(15) }
    return pg_pay(variant, "11", amount=amount, first_name=first_name,
                  last_name=last_name, client_token=client_token,
                  payment_token=payment_token, dict_extras=random_order_id)

def void_via_cc(variant, authorization_code, trace_number):
    # void the auth
    extras_dict = { 'pg_original_authorization_code': authorization_code,
                    'pg_original_trace_number': trace_number, }
    return pg_pay(variant, "14", dict_extras=extras_dict)

def capture_via_cc(variant, authorization_code, trace_number):
    # void the auth
    extras_dict = { 'pg_original_authorization_code': authorization_code,
                    'pg_original_trace_number': trace_number, }
    return pg_pay(variant, "12", dict_extras=extras_dict)

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
            time_window = datetime.datetime.now() - datetime.timedelta(hours=18)
            past_variants = models.PaymentsGatewayVariant.objects.filter(
                Q(pg_client_token=form.cleaned_data['pg_client_token']) |
                Q(pg_payment_token=form.cleaned_data['pg_payment_token']),
                reused_by__isnull=True,
                receipt__creation_time__gt=time_window,
                order__ssorder__appointment=order.ssorder.appointment,
                amount=form.cleaned_data['amount'],
                receipt__pg_response_code='A01',
                receipt__pg_transaction_type='11')\
                .order_by("-receipt__creation_time")
            variant_ref = form.save()
            amount = str(variant_ref.amount.quantize(Decimal('.01')))

            if past_variants:
                past_variant = past_variants[0]
                variant_ref.pg_authorization_code = \
                    past_variant.pg_authorization_code
                variant_ref.pg_trace_number = past_variant.pg_trace_number
                past_variant.reused_by = variant_ref
                past_variant.save()
            else:
                if variant_ref.amount > 0:
                    if variant_ref.pg_payment_token:
                        auth_via_cc(variant_ref, amount,
                                    first_name=variant_ref.token_first_name,
                                    last_name=variant_ref.token_last_name,
                                    payment_token=variant_ref.pg_payment_token)
                    elif variant_ref.pg_client_token:
                        auth_via_cc(variant_ref, amount,
                                    client_token=variant_ref.pg_client_token)
                    else:
                        raise PaymentFailure(_("Payment or Client Token Required"))
                    variant_ref.pg_authorization_code = \
                        variant_ref.receipt.pg_authorization_code
                    variant_ref.pg_trace_number = \
                        variant_ref.receipt.pg_trace_number
            variant_ref.save()
            return variant_ref
        raise PaymentFailure(_("Could not create PaymentsGateway Variant"))

    def confirm(self, order, typ=None, variant=None):
        if not variant:
            variant = order.paymentvariant
        v = variant.get_subtype_instance()
        if v.amount > 0:
            capture_via_cc(v, v.pg_authorization_code, v.pg_trace_number)
