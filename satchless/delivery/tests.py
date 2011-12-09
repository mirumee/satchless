# -*- coding:utf-8 -*-
from django.utils.translation import ugettext
import django.db
import django.forms

from . import DeliveryProvider, DeliveryType
from ..order.forms import DeliveryMethodForm, DeliveryDetailsForm
from ..order.tests import order_app


class TestDeliveryVariant(django.db.models.Model):
    email = django.db.models.EmailField()
    delivery_group = django.db.models.OneToOneField(order_app.DeliveryGroup)


class DeliveryForm(django.forms.ModelForm):
    class Meta:
        model = TestDeliveryVariant
        fields = ('email',)


class TestDeliveryMethodForm(DeliveryMethodForm):
    class Meta:
        fields = ('delivery_type',)
        model = order_app.DeliveryGroup


class TestDeliveryDetailsForm(DeliveryDetailsForm):
    class Meta:
        exclude = ('delivery_type',)
        model = order_app.DeliveryGroup


class TestDeliveryProvider(DeliveryProvider):
    def __init__(self, delivery_types=None):
        # by default this is one type delivery provider
        self.types = delivery_types or (DeliveryType('pidgin', 'pidgin'), )

    def __unicode__(self):
        return ugettext("Test delivery")

    def enum_types(self, delivery_group=None, customer=None):
        for typ in self.types:
            yield self, typ

    def get_configuration_form(self, delivery_group, data, typ=None):
        typ = typ or delivery_group.delivery_type
        instance = TestDeliveryVariant(delivery_group=delivery_group)
        return DeliveryForm(data or None, instance=instance)

    def save(self, delivery_group, form=None, typ=None):
        typ = typ or delivery_group.delivery_type
        delivery_group.delivery_price = 20
        delivery_group.delivery_type_name = typ
        delivery_group.save()
        form.save()