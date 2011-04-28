from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module

_partitioners_queue = None
_delivery_providers_queue = None
_payment_providers_queue = None

def partition(cart):
    groups = []
    remaining_items = list(cart.items.all())
    for handler in _partitioners_queue:
        handled_groups, remaining_items = handler.partition(cart,
                                                            remaining_items)
        groups += handled_groups
    if remaining_items:
        raise ImproperlyConfigured('Unhandled items remaining in cart.')
    return groups

def get_delivery_types(delivery_group):
    types = []
    for provider_path, provider in _delivery_providers_queue:
        prov_types = provider.enum_types(delivery_group=delivery_group)
        types.extend([('%s:%s' % (provider_path, t[0]), t[1]) for t in prov_types])
    return types

def get_delivery_provider(typ):
    provider_path, typ_short = typ.split(':', 1)
    for prov_path, provider in _delivery_providers_queue:
        if provider_path == prov_path:
            return provider, typ_short
    raise ValueError('No provider found for delivery type %s.' % typ)

def get_delivery_formclass(delivery_group, typ):
    provider, typ_short = get_delivery_provider(typ)
    return provider.get_formclass(delivery_group, typ_short)

def get_delivery_variant(delivery_group, typ, form):
    provider, typ_short = get_delivery_provider(typ)
    return provider.get_variant(delivery_group, typ_short, form)

def get_payment_types(order):
    types = []
    for provider_path, provider in _payment_providers_queue:
        prov_types = provider.enum_types(order=order)
        types.extend([('%s:%s' % (provider_path, t[0]), t[1]) for t in prov_types])
    return types

def get_payment_provider(typ):
    provider_path, typ_short = typ.split(':', 1)
    for prov_path, provider in _payment_providers_queue:
        if provider_path == prov_path:
            return provider, typ_short
    raise ValueError('No provider found for payment type %s.' % typ)

def get_payment_formclass(order, typ):
    provider, typ_short = get_payment_provider(typ)
    return provider.get_configuration_formclass(order, typ_short)

def get_payment_variant(order, typ, form):
    provider, typ_short = get_payment_provider(typ)
    return provider.get_variant(order, typ_short, form)

def get_confirmation_formdata(order, typ):
    provider, typ_short = get_payment_provider(typ)
    return provider.get_confirmation_formdata(order)

def init_queues():
    global _partitioners_queue
    _partitioners_queue = []
    handlers = getattr(settings, 'SATCHLESS_ORDER_PARTITIONERS', [
        'satchless.contrib.order.partitioner.simple',
    ])
    for handler_setting in handlers:
        if isinstance(handler_setting, str):
            mod_name, han_name = handler_setting.rsplit('.', 1)
            module = import_module(mod_name)
            handler = getattr(module, han_name)
        else:
            handler = handler_setting
        if not callable(getattr(handler, 'partition', None)):
            raise ImproperlyConfigured(
                '%s in SATCHLESS_ORDER_PARTITIONERS does not implement partition() method' %\
                        handler_setting)
        _partitioners_queue.append(handler)

    def build_q_from_paths(setting_name, required_methods):
        queue = []
        elements = getattr(settings, setting_name, [])
        for e in elements:
            if isinstance(e, str):
                mod_name, obj_name = e.rsplit('.', 1)
                module = import_module(mod_name)
                e_obj = getattr(module, obj_name)
                queue.append((e, e_obj))
            else:
                raise ValueError('%r in %s is not a proper Python path' % \
                        (e, setting_name))
            for method in required_methods:
                if not callable(getattr(e_obj, method, None)):
                    raise ImproperlyConfigured('%s in %s does not implement %s() method' % (
                            e, setting_name, method))
        return queue

    global _delivery_providers_queue
    _delivery_providers_queue = build_q_from_paths(
            'SATCHLESS_DELIVERY_PROVIDERS', ('enum_types', 'get_formclass', 'get_variant'))
    global _payment_providers_queue
    _payment_providers_queue = build_q_from_paths(
            'SATCHLESS_PAYMENT_PROVIDERS',
            ('enum_types', 'get_configuration_formclass', 'get_variant', 'get_confirmation_formdata'))

init_queues()
