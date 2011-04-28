from django.conf import settings
import payments

from satchless.payment import PaymentProvider, ConfirmationFormNeeded
from . import models

class DjangoPaymentsProvider(PaymentProvider):
    def enum_types(self, order=None, customer=None):
        payment_types = getattr(settings, 'SATCHLESS_DJANGO_PAYMENT_TYPES', None)
        if payment_types:
            payment_types = ((k,k) for k in payment_types)
        else:
            payment_types = ()
        return payment_types

    def get_variant(self, order, typ, form):
        factory = payments.factory(typ)
        payment = factory.create_payment(currency=order.currency, total=order.total().gross)
        payment_variant = models.DjangoPaymentsVariant.objects \
                                .create(payment=payment, order=order, price=0)
        return payment_variant

    def confirm(self, order):
        form = order.paymentvariant.get_subtype_instance().payment.get_form()
        raise ConfirmationFormNeeded(form, form.action, form.method)

provider = DjangoPaymentsProvider()
