from django.utils.translation import ugettext

from ....delivery import DeliveryProvider, DeliveryType
from . import forms
from . import models

class PostDeliveryProvider(DeliveryProvider):
    form_class = forms.PostShippingVariantForm

    def __unicode__(self):
        return ugettext("Post delivery")

    def enum_types(self, customer=None, delivery_group=None):
        filter_kwargs = {}
        if delivery_group and hasattr(delivery_group, 'postshippingvariant_set'):
            shipping_regions = DeliveryCountry.objects.filter(
                code__in=delivery_group.postshippingvariant_set.values_list('shipping_country', flat=True)
            ).values_list('region', flat=True)
            if shipping_regions:
                filter_kwargs['region__id__in'] = shipping_regions
        for record in models.PostShippingType.objects.filter(**filter_kwargs):
            yield self, DeliveryType(typ=record.typ, name=record.name)

    def get_configuration_form(self, delivery_group, typ, data):
        typ = models.PostShippingType.objects.get(typ=typ)
        instance = models.PostShippingVariant(delivery_group=delivery_group,
                                              name=typ.name,
                                              price=typ.price)
        return self.form_class(data or None, instance=instance,
                               prefix='delivery_group-%d' %
                               delivery_group.pk)

    def create_variant(self, delivery_group, typ, form):
        return form.save()
