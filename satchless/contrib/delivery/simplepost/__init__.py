from django.utils.translation import ugettext

from ....delivery import DeliveryProvider, DeliveryType
from . import models


class PostDeliveryProvider(DeliveryProvider):
    def __unicode__(self):
        return ugettext("Post delivery")

    def enum_types(self, customer=None, delivery_group=None):
        for record in models.PostShippingType.objects.all():
            if not delivery_group or delivery_group.require_shipping_address:
                yield DeliveryType(provider=self, typ=record.typ,
                                   name=record.name)

    def save(self, delivery_group, typ, form):
        typ = models.PostShippingType.objects.get(typ=typ)
        delivery_group.delivery_type_name = typ.name
        delivery_group.delivery_price = typ.price
        delivery_group.save()
