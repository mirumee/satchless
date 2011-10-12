from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from urllib import urlencode
from urlparse import parse_qs

from satchless.core.handler import QueueHandler

from ..delivery import DeliveryProvider
from ..delivery.models import DeliveryVariant
from ..payment import PaymentProvider
from ..payment.models import PaymentVariant
from . import Partitioner


### PARTITIONERS
partitioners = getattr(settings, 'SATCHLESS_ORDER_PARTITIONERS', [
    'satchless.contrib.order.partitioner.simple',
])

class PartitionerQueue(Partitioner, QueueHandler):
    element_class = Partitioner
    require_unique_id = True

    def partition(self, cart):
        groups = []
        remaining_items = list(cart.items.all())
        for handler in self.queue:
            handled_groups, remaining_items = handler.partition(cart,
                                                                remaining_items)
            groups += handled_groups
        if remaining_items:
            raise ImproperlyConfigured('Unhandled items remaining in cart.')
        return groups

partitioners_queue = PartitionerQueue(*partitioners)


### PAYMENT PROVIDERS
if not getattr(settings, 'SATCHLESS_PAYMENT_PROVIDERS', None):
    raise ImproperlyConfigured('You need to configure '
                               'SATCHLESS_PAYMENT_PROVIDERS')

class PaymentQueue(PaymentProvider, QueueHandler):
    element_class = PaymentProvider
    require_unique_id = True

    def enum_types(self, order=None, customer=None):
        for unique_id, provider in self.queue:
            types = provider.enum_types(order=order)
            for typ in types:
                yield typ

    def get_configuration_form(self, order, data):
        provider, typ_short = self.get_provider(order.payment_type)
        return provider.get_configuration_form(order=order, typ=typ_short, data=data)

    def create_variant(self, order, typ, form):
        provider, typ_short = self.get_provider(order.payment_type)
        try:
            order.paymentvariant.delete()
        except PaymentVariant.DoesNotExist:
            pass
        return provider.create_variant(order, typ_short, form)

    def confirm(self, order):
        provider, typ_short = self.get_provider(order.payment_type)
        return provider.confirm(order)

payment_queue = PaymentQueue(*settings.SATCHLESS_PAYMENT_PROVIDERS)


### DELIVERY PROVIDERS
if not getattr(settings, 'SATCHLESS_DELIVERY_PROVIDERS', None):
    raise ImproperlyConfigured('You need to configure '
                               'SATCHLESS_DELIVERY_PROVIDERS')

class DeliveryQueue(DeliveryProvider, QueueHandler):
    element_class = DeliveryProvider
    require_unique_id = True

    def enum_types(self, delivery_group):
        result = []
        for provider_id, provider in self.queue:
            types = provider.enum_types(delivery_group=delivery_group)
            for type_id, type_name in types:
                data = {
                    'provider': provider_id,
                    'type': type_id,
                }
                result.append((urlencode(data), type_name))
        return result

    def get_delivery_form(self, delivery_group, data):
        provider = self.get_provider(delivery_group.delivery_provider)
        return provider.get_configuration_form(delivery_group, data)

    def create_delivery_variant(self, delivery_group, form):
        provider = self.get_provider(delivery_group.delivery_provider)
        # XXX: Do we really need it here?
        try:
            delivery_group.deliveryvariant.delete()
        except DeliveryVariant.DoesNotExist:
            pass
        return provider.create_variant(delivery_group, form)

delivery_queue = DeliveryQueue(*settings.SATCHLESS_DELIVERY_PROVIDERS)
