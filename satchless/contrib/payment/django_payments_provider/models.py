from django.db import models
from payments.models import Payment

class DjangoPaymentsPayment(models.Model):

    payment = models.OneToOneField(Payment,
                                   related_name='satchless_payment_variant')

    class Meta:
        abstract = True

    def __unicode__(self):
        return "%s %s @ %s%s (via django-payments)" % (
            self.payment.get_status_display(),
            self.payment.variant,
            self.payment.total,
            self.payment.currency)
