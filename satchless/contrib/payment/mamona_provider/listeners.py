from django.core.urlresolvers import reverse

from satchless.order.models import OrderedItem

from mamona import signals

def payment_status_changed_listener(sender, instance=None, old_status=None, new_status=None, **kwargs):
    if new_status == 'paid':
        instance.order.order.set_status('payment-complete')
    elif new_status == 'failed':
        instance.order.order.set_status('payment-failed')

def return_urls_query_listener(sender, instance=None, urls=None, **kwargs):
    urls['failure'] = urls['paid'] = reverse(
                'satchless-order-view',
                kwargs={'order_token': instance.order.order.token})

def order_items_query_listener(sender, instance=None, items=None, **kwargs):
    for item in OrderedItem.objects.filter(delivery_group__order=instance.order.order):
        items.append({'name': item.product_name, 'quantity': item.quantity,
                'unit_price': item.unit_price_gross})

def start_listening():
    signals.payment_status_changed.connect(payment_status_changed_listener)
    signals.return_urls_query.connect(return_urls_query_listener)
    signals.order_items_query.connect(order_items_query_listener)
