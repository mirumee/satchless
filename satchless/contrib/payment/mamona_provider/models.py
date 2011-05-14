from django.core.exceptions import ObjectDoesNotExist
from mamona.models import build_payment_model
from satchless.payment.models import PaymentVariant

class MamonaPaymentVariant(PaymentVariant):
    def __unicode__(self):
        try:
            payment = self.payments.get()
        except ObjectDoesNotExist:
            return u"(empty mamona payment)"
        if payment.status == 'paid':
            return u"%.2f %s via %s on %s (by mamona)" % (
                    payment.amount,
                    payment.get_status_display(),
                    payment.backend,
                    payment.paid_on)
        else:
            return u"%.2f %s via %s created on %s (by mamona)" % (
                    payment.amount,
                    payment.get_status_display(),
                    payment.backend,
                    payment.created_on)

Payment = build_payment_model(MamonaPaymentVariant, unique=True, related_name='payments')
