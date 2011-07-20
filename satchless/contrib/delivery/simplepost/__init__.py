from django.utils.translation import ugettext as _
from satchless.delivery import DeliveryProvider

from . import forms
from . import models

class PostDeliveryProvider(DeliveryProvider):
    unique_id = 'post'

    def __unicode__(self):
        return _("Post delivery")

    def enum_types(self, customer=None, delivery_group=None):
        return ([(t.typ, t.name) for t in models.PostShippingType.objects.all()])

    def get_configuration_form(self, delivery_group, typ, data):
        typ = models.PostShippingType.objects.get(typ=typ)
        instance = models.PostShippingVariant(delivery_group=delivery_group,
                                              name=typ.name,
                                              price=typ.price)
        return forms.PostShippingVariantForm(data or None, instance=instance,
                                             prefix='delivery_group-%d' %
                                             delivery_group.pk)

    def create_variant(self, delivery_group, typ, form):
        return form.save()
