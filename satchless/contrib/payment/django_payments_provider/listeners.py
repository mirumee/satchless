from payments import signals
from . import models

def payment_status_changed_listener(sender, instance=None, **kwargs):
    try:
        variant = instance.satchless_payment_variant
    except models.DjangoPaymentsVariant.DoesNotExist:
        return
    order = variant.orders.get()
    if instance.status == 'confirmed':
        order.set_status('payment-complete')
    elif instance.status == 'rejected':
        order.set_status('cancelled')

signals.status_changed.connect(payment_status_changed_listener)
