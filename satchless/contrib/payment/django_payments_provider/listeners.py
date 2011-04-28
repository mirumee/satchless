from payments import signals
from . import models

def payment_status_changed_listener(sender, instance=None, **kwargs):
    try:
        variant = instance.satchless_payment_variant
    except models.DjangoPaymentsVariant.DoesNotExist:
        return
    if instance.status == 'confirmed':
        variant.order.set_status('payment-complete')
    elif instance.status == 'rejected':
        variant.order.set_status('payment-failed')

signals.status_changed.connect(payment_status_changed_listener)
