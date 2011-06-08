from django.conf import settings
import payments

from satchless.payment import PaymentProvider, ConfirmationFormNeeded
from . import listeners
from . import models

class DjangoPaymentsProvider(PaymentProvider):
    unique_id = 'django-payments'

    def enum_types(self, order=None, customer=None):
        return getattr(settings, 'SATCHLESS_DJANGO_PAYMENT_TYPES', ())

    def create_variant(self, order, typ, form):
        factory = payments.factory(typ)
        payment = factory.create_payment(currency=order.currency,
                                         total=order.total().gross)
        payment_variant = models.DjangoPaymentsVariant.objects.create(
                payment=payment, order=order, price=0)
        return payment_variant

    def confirm(self, order):
        form = order.paymentvariant.get_subtype_instance().payment.get_form()
        raise ConfirmationFormNeeded(form, form.action, form.method)

listeners.start_listening()
