from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
import payments
from payments import signals

from ....payment import (PaymentProvider, ConfirmationFormNeeded,
                         PaymentType)


class DjangoPaymentsProvider(PaymentProvider):
    payment_class = None

    def __init__(self, *args, **kwargs):
        super(DjangoPaymentsProvider, self).__init__(*args, **kwargs)
        assert self.payment_class
        self.start_listening()

    def enum_types(self, order=None, customer=None):
        for typ, name in settings.SATCHLESS_DJANGO_PAYMENT_TYPES:
            yield PaymentType(provider=self, typ=typ, name=name)

    def save(self, order, form, typ=None):
        typ = typ or order.payment_type
        factory = payments.factory(typ)
        payment = factory.create_payment(
            currency=settings.SATCHLESS_DEFAULT_CURRENCY,
            total=order.get_total().gross)
        payment_variant = self.payment_class.objects.create(
                payment=payment, order=order)
        return payment_variant

    def confirm(self, order, typ=None):
        form = order.paymentvariant.payment.get_form()
        raise ConfirmationFormNeeded(form, form.action, form.method)

    def on_payment_status_changed(self, sender, instance=None, **kwargs):
        try:
            variant = self.payment_class.objects.get(
                order=instance.satchless_payment_variant.order)
        except ObjectDoesNotExist:
            return
        if instance.status == 'confirmed':
            variant.order.set_status('payment-complete')
        elif instance.status == 'rejected':
            variant.order.set_status('payment-failed')

    def start_listening(self):
        signals.status_changed.connect(self.on_payment_status_changed)
