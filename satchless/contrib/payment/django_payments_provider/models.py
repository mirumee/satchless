from django.db import models

from satchless.payment.models import PaymentVariant

class DjangoPaymentsVariant(PaymentVariant):
    payment = models.OneToOneField(PaymentVariant,
                                   related_name='satchless_payment_variant')
