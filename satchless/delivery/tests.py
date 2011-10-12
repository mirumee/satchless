# -*- coding:utf-8 -*-
from django.utils.translation import ugettext as _
import django.db
import django.forms

from . import models
from . import DeliveryProvider, DeliveryType


class TestDeliveryVariant(models.DeliveryVariant):
    email = django.db.models.EmailField()


class DeliveryForm(django.forms.ModelForm):
    class Meta:
        model = TestDeliveryVariant
        fields = ('email',)


class TestDeliveryProvider(DeliveryProvider):
    def __init__(self, delivery_types=None):
        # by default this is one type delivery provider
        self.types = delivery_types or (DeliveryType('pidgin', 'pidgin'), )

    def __unicode__(self):
        return _("Test delivery")

    def enum_types(self, delivery_group=None, customer=None):
        for typ in self.types:
            yield self, typ

    def get_configuration_form(self, delivery_group, data, typ=None):
        typ = typ or delivery_group.delivery_type
        instance = TestDeliveryVariant(delivery_group=delivery_group,
                                       name=typ, price=20)
        return DeliveryForm(data or None, instance=instance)

    def create_variant(self, delivery_group, form=None, typ=None):
        return form.save()