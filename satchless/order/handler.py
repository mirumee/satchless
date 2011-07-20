from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module
from urllib import urlencode
from urlparse import parse_qs

from ..delivery import DeliveryProvider
from ..delivery.models import DeliveryVariant
from ..payment import PaymentProvider
from ..payment.models import PaymentVariant

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
    result = []
    for provider_id, provider in _delivery_providers_queue:
        types = provider.enum_types(delivery_group=delivery_group)
        for type_id, type_name in types:
            data = {
                'provider': provider_id,
                'type': type_id,
            }
            result.append((urlencode(data), type_name))
    return result

def get_delivery_type_name(typ):
    provider, short_typ = get_delivery_provider(typ)
    delivery_types = dict(provider.enum_types())
    return delivery_types[short_typ]

def get_delivery_provider(typ):
    data = parse_qs(typ)
    provider_id = data.get('provider', [None]).pop()
    type_name = data.get('type', [None]).pop()
    if not provider_id or not type_name:
        raise ValueError('Malformed delivery type: %s.' % typ)
    provider_dict = dict(_delivery_providers_queue)
    provider = provider_dict.get(provider_id)
    if not provider:
        raise ValueError('No provider found for delivery type %s.' % typ)
    return provider, type_name

def get_delivery_form(delivery_group, data):
    provider, typ_short = get_delivery_provider(delivery_group.delivery_type)
    return provider.get_configuration_form(delivery_group, typ_short, data)

def create_delivery_variant(delivery_group, form):
    provider, typ_short = get_delivery_provider(delivery_group.delivery_type)
    try:
        delivery_group.deliveryvariant.delete()
    except DeliveryVariant.DoesNotExist:
        pass
    return provider.create_variant(delivery_group, typ_short, form)

def get_payment_types(order):
    result = []
    for provider_id, provider in _payment_providers_queue:
        types = provider.enum_types(order=order)
        for type_id, type_name in types:
            data = {
                'provider': provider_id,
                'type': type_id,
            }
            result.append((urlencode(data), type_name))
    return result

def get_payment_provider(typ):
    data = parse_qs(typ)
    provider_id = data.get('provider', [None]).pop()
    type_name = data.get('type', [None]).pop()
    if not provider_id or not type_name:
        raise ValueError('Malformed payment type: %s.' % typ)
    provider_dict = dict(_payment_providers_queue)
    provider = provider_dict.get(provider_id)
    if not provider:
        raise ValueError('No provider found for payment type %s.' % typ)
    return provider, type_name

def get_payment_form(order, data):
    provider, typ_short = get_payment_provider(order.payment_type)
    return provider.get_configuration_form(order, typ_short, data)

def create_payment_variant(order, form):
    provider, typ_short = get_payment_provider(order.payment_type)
    try:
        order.paymentvariant.delete()
    except PaymentVariant.DoesNotExist:
        pass
    return provider.create_variant(order, typ_short, form)

def confirm(order):
    provider, typ_short = get_payment_provider(order.payment_type)
    return provider.confirm(order)

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
            raise ImproperlyConfigured('%s in SATCHLESS_ORDER_PARTITIONERS '
                                       'does not implement partition() method' %
                                       handler_setting)
        _partitioners_queue.append(handler)

    def build_q_from_paths(setting_name, required_type):
        queue = []
        registered_ids = set()
        elements = getattr(settings, setting_name, [])
        for item in elements:
            if isinstance(item, str):
                mod_name, attr_name = item.rsplit('.', 1)
                module = import_module(mod_name)
                if not hasattr(module, attr_name):
                    raise ImproperlyConfigured(
                        '%s in %s does not exist.' % (item, setting_name))
                item = getattr(module, attr_name)
            if isinstance(item, type):
                item = item()
            if not isinstance(item, required_type):
                raise ImproperlyConfigured('%r in %s is not a proper subclass '
                                           'of %s' %
                                           (item, setting_name,
                                            required_type.__name__))
            if not item.unique_id:
                raise ImproperlyConfigured('%r in %s does not have a unique '
                                           'ID.' % (item, setting_name))
            if item.unique_id in registered_ids:
                previous = dict(queue).get(item.unique_id)
                raise ImproperlyConfigured('%r in %s provides an ID of %s that '
                                           'was already claimed by %r. Did you '
                                           'include the same object twice?' %
                                           (item, setting_name, item.unique_id,
                                            previous))
            registered_ids.add(item.unique_id)
            queue.append((item.unique_id, item))
        return queue

    global _delivery_providers_queue
    _delivery_providers_queue = build_q_from_paths(
            'SATCHLESS_DELIVERY_PROVIDERS', DeliveryProvider)
    global _payment_providers_queue
    _payment_providers_queue = build_q_from_paths(
            'SATCHLESS_PAYMENT_PROVIDERS', PaymentProvider)

init_queues()
