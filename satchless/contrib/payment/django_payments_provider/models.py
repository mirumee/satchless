from django.db import models

from payments.models import Payment
from satchless.payment.models import PaymentVariant

class DjangoPaymentsVariant(PaymentVariant):
    payment = models.OneToOneField(Payment, related_name='satchless_payment_variant')
