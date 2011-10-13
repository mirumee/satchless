from django.db import models
from payments.models import Payment

from ....payment.models import PaymentVariant

class DjangoPaymentsVariant(PaymentVariant):
    payment = models.OneToOneField(Payment, related_name='satchless_payment_variant')

    def __unicode__(self):
        return "%s %s @ %s%s (via django-payments)" % (
                self.payment.get_status_display(),
                self.payment.variant,
                self.payment.total,
                self.payment.currency)
