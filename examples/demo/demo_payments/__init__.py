from satchless.contrib.payment.django_payments_provider import DjangoPaymentsProvider

from . import models

class PaymentsProvider(DjangoPaymentsProvider):

    payment_class = models.Payment
