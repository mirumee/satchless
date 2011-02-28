from django.conf import settings
import payments

from satchless.payment import PaymentProvider
from . import models

class DjangoPaymentsProvider(PaymentProvider):
    def enum_types(self, order=None, customer=None):
        payment_types = getattr(settings, 'SATCHLESS_DJANGO_PAYMENT_TYPES', None)
        if not payment_types:
            payment_types = ()
        return payment_types

    def get_variant(self, order, typ, form):
        factory = payments.factory(typ)
        payment = factory.create_payment(currency=order.currency)
        payment_variant = models.DjangoPaymentsVariant.objects \
                                                      .create(payment=payment)
        return payment_variant

    def get_confirmation_form(self, order, variant):
        form = variant.payment.get_form()
        return {'form': form,
                'action': form.action,
                'method': form.method}
