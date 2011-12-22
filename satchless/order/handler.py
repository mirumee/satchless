from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from satchless.core.handler import QueueHandler

from ..delivery import DeliveryProvider, DeliveryType
from ..payment import PaymentProvider, PaymentType
from . import Partitioner

### PARTITIONERS
class PartitionerQueue(Partitioner, QueueHandler):
    element_class = Partitioner

    def partition(self, cart, items=None):
        groups = []
        remaining_items = items or list(cart.get_all_items())
        for handler in self.queue:
            handled_groups, remaining_items = handler.partition(cart,
                                                                remaining_items)
            groups += handled_groups
        if remaining_items:
            raise ImproperlyConfigured('Unhandled items remaining in cart.')
        return groups


partitioners = getattr(settings, 'SATCHLESS_ORDER_PARTITIONERS', [
    'satchless.contrib.order.partitioner.simple.SimplePartitioner',
])
partitioner_queue = PartitionerQueue(*partitioners)


### PAYMENT PROVIDERS
class PaymentQueue(PaymentProvider, QueueHandler):
    element_class = PaymentProvider

    def enum_types(self, order=None, customer=None):
        for provider in self.queue:
            types = provider.enum_types(order=order, customer=customer)
            for typ in types:
                if not isinstance(typ, PaymentType):
                    raise ValueError('Payment types must be instances of'
                                     ' PaymentType type, not %s.' %
                                     (repr(typ, )))
                yield typ

    def _get_provider(self, order, typ):
        for payment_type in self.enum_types(order):
            if payment_type.typ == typ:
                return payment_type.provider
        raise ValueError('Unable to find a payment provider for type %s' %
                         (typ, ))

    def get_configuration_form(self, order, data, typ=None):
        typ = typ or order.payment_type
        provider = self._get_provider(order, typ)
        return provider.get_configuration_form(order=order, data=data, typ=typ)

    def save(self, order, form, typ=None):
        typ = typ or order.payment_type
        provider = self._get_provider(order, typ)
        return provider.save(order=order, form=form, typ=typ)

    def confirm(self, order, typ=None):
        typ = typ or order.payment_type
        provider = self._get_provider(order, typ)
        return provider.confirm(order=order, typ=typ)


payment_providers = getattr(settings, 'SATCHLESS_PAYMENT_PROVIDERS', [])
payment_queue = PaymentQueue(*payment_providers)


### DELIVERY PROVIDERS
class DeliveryQueue(DeliveryProvider, QueueHandler):
    element_class = DeliveryProvider

    def enum_types(self, delivery_group=None, customer=None):
        for provider in self.queue:
            types = provider.enum_types(delivery_group=delivery_group,
                                        customer=customer)
            for typ in types:
                if not isinstance(typ, DeliveryType):
                    raise ValueError('Delivery types must be instances of'
                                     ' DeliveryType type, not %s.' %
                                     (repr(typ, )))
                yield typ

    def _get_provider(self, delivery_group, typ):
        for delivery_type in self.enum_types(delivery_group):
            if delivery_type.typ == typ:
                return delivery_type.provider
        raise ValueError('Unable to find a delivery provider for type %s' %
                         (typ, ))

    def get_configuration_form(self, delivery_group, data, typ=None):
        typ = typ or delivery_group.delivery_type
        provider = self._get_provider(delivery_group, typ)
        return provider.get_configuration_form(delivery_group=delivery_group,
                                               data=data, typ=typ)

    def save(self, delivery_group, form, typ=None):
        typ = typ or delivery_group.delivery_type
        provider = self._get_provider(delivery_group, typ)
        return provider.save(delivery_group=delivery_group, form=form, typ=typ)


delivery_providers = getattr(settings, 'SATCHLESS_DELIVERY_PROVIDERS', [])
delivery_queue = DeliveryQueue(*delivery_providers)