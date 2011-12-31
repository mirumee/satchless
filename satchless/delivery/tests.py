# -*- coding:utf-8 -*-
import django.db
import django.forms

from . import DeliveryProvider, DeliveryType
from ..order.tests import order_app


class TestDeliveryType(django.db.models.Model):
    name = django.db.models.CharField(max_length=256)
    typ = django.db.models.CharField(max_length=256)
    price = django.db.models.DecimalField(default=0, max_digits=12,
                                          decimal_places=4)
    with_customer_notes = django.db.models.BooleanField(
        default=False, help_text=u'Allow user to add additional '
                                  'delivery information')


class TestDeliveryVariant(django.db.models.Model):
    delivery_group = django.db.models.OneToOneField(order_app.DeliveryGroup)
    price = django.db.models.DecimalField(default=0, max_digits=12, decimal_places=4)
    notes = django.db.models.TextField(max_length=120, blank=True)


class TestDeliveryDetailsForm(django.forms.ModelForm):
    class Meta:
        model = TestDeliveryVariant
        fields = ('notes',)


class TestDeliveryProvider(DeliveryProvider):
    def __unicode__(self):
        return "Test delivery"

    def enum_types(self, delivery_group=None, customer=None):
        for delivery_type in TestDeliveryType.objects.all():
            yield DeliveryType(self, typ=delivery_type.typ,
                                    name=delivery_type.name)

    def get_configuration_form(self, delivery_group, data, typ=None):
        typ = typ or delivery_group.delivery_type
        try:
            delivery_type = TestDeliveryType.objects.get(typ=typ)
        except TestDeliveryType.DoesNotExists:
            raise ValueError('Unable to find a delivery type: %s' %
                             (typ, ))

        instance = TestDeliveryVariant(delivery_group=delivery_group,
                                       price=delivery_type.price)
        if delivery_type.with_customer_notes:
            return TestDeliveryDetailsForm(data or None, instance=instance)

    def save(self, delivery_group, form=None, typ=None):
        if form:
            form.save()
        else:
            try:
                delivery_type = TestDeliveryType.objects.get(typ=typ)
            except TestDeliveryType.DoesNotExists:
                raise ValueError('Unable to find a delivery type: %s' %
                                 (typ, ))
            TestDeliveryVariant.objects.create(
                delivery_group=delivery_group, price=delivery_type.price)


