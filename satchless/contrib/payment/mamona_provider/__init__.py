from django.conf import settings
from mamona.utils import get_backend_choices

from satchless.payment import PaymentProvider
from . import models

class MamonaProvider(PaymentProvider):
    def enum_types(self, order=None, customer=None):
        return get_backend_choices()

    def get_variant(self, order, typ, form):
        variant = models.MamonaPaymentVariant.objects\
                .get_or_create(order=order, price=0)[0]
        payment = models.Payment.objects\
                .create(order=variant, amount=order.total().gross,
                        currency=order.currency, backend=typ)
        return variant

    def get_confirmation_formdata(self, order):
        payment = order.paymentvariant.get_subtype_instance().payments.get()
        return payment.get_processor().get_confirmation_form(payment)

provider = MamonaProvider()
