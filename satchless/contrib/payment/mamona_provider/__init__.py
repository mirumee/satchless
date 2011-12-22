from django.core.urlresolvers import reverse
from mamona import signals
from mamona.utils import get_backend_choices
from ....payment import (PaymentProvider, ConfirmationFormNeeded,
                         PaymentType)

class MamonaProvider(PaymentProvider):
    payment_class = None

    def __init__(self, *args, **kwargs):
        super(MamonaProvider, self).__init__(*args, **kwargs)
        assert self.payment_class
        self.start_listening()

    def enum_types(self, order=None, customer=None):
        for typ, name in get_backend_choices():
            yield PaymentType(provider=self, typ=typ, name=name)

    def save(self, order, typ, form):
        payment_type = [t.name for t in self.enum_types() if t.typ == typ][0]
        order.payment_type_price = 0
        order.payment_type_name = payment_type.name
        self.payment_class.objects.create(order=order,
                                          amount=order.get_total().gross,
                                          currency=order.currency, backend=typ)

    def confirm(self, order, typ):
        payment = order.paymentvariant.get_subtype_instance().payments.get()
        form = payment.get_processor().get_confirmation_form(payment)
        raise ConfirmationFormNeeded(**form)

    def on_payment_status_changed(sender, instance=None, old_status=None,
                                  new_status=None, **kwargs):
        if new_status == 'paid':
            instance.order.order.set_status('payment-complete')
        elif new_status == 'failed':
            instance.order.order.set_status('payment-failed')

    def on_return_urls_query(self, sender, instance=None, urls=None,
                             **kwargs):
        urls['failure'] = urls['paid'] = reverse(
            'order:details', kwargs={'order_token': instance.order.order.token})

    def on_order_items_query(self, sender, instance=None, items=None,
                             **kwargs):
        satchless_order = instance.order.get_subtype_instance().order
        ordered_item = satchless_order.get_ordered_item_class()
        for item in ordered_item.objects.filter(
            delivery_group__order=satchless_order):
            items.append({'name': item.product_name, 'quantity': item.quantity,
                          'unit_price': item.unit_price_gross})

    def start_listening(self):
        signals.payment_status_changed.connect(self.on_payment_status_changed)
        signals.return_urls_query.connect(self.on_return_urls_query)
        signals.order_items_query.connect(self.on_order_items_query)