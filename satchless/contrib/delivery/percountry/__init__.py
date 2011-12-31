from django.utils.translation import ugettext

from ....delivery import DeliveryProvider, DeliveryType
from . import models

class PostDeliveryProvider(DeliveryProvider):
    def __unicode__(self):
        return ugettext("Post delivery")

    def enum_types(self, customer=None, delivery_group=None):
        filter_kwargs = {}
        if delivery_group:
            filter_kwargs['region__deliverycountry__code'] = delivery_group.shipping.shipping_country
        for record in models.PostShippingType.objects.filter(**filter_kwargs):
            yield DeliveryType(provider=self, typ=record.typ, name=record.name)

    def create_variant(self, delivery_group, typ, form):
        typ = models.PostShippingType.objects.get(typ=typ)
        delivery_group.delivery_type_name = typ.name
        delivery_group.delivery_price = typ.price
        delivery_group.save()