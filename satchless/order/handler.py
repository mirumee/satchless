from django.conf import settings
from django.utils.importlib import import_module

_handlers_queue = None

def partition(cart):
    groups = []
    remaining_items = list(cart.items.all())
    for handler in _handlers_queue:
        handled_groups, remaining_items = handler.partition(cart,
                                                            remaining_items)
        groups += handled_groups
    if remaining_items:
        raise ImproperlyConfigured('Unhandled items remaining in cart.')
    return groups

def init_queue():
    global _handlers_queue
    _handlers_queue = []
    handlers = getattr(settings, SATCHLESS_ORDER_PARTITIONERS, [
        'satchless.contrib.order.partitioner.simple',
    ])
    for handler in handlers:
        if isinstance(handler, str):
            mod_name, han_name = handler.rsplit('.', 1)
            module = import_module(mod_name)
            handler = getattr(module, han_name)
        _handlers_queue.append(handler)

init_queue()
