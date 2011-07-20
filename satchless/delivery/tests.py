# -*- coding:utf-8 -*-
from django.utils.translation import ugettext as _
import django.db
import django.forms

from . import models
from . import DeliveryProvider


class TestDeliveryVariant(models.DeliveryVariant):
    email = django.db.models.EmailField()


class DeliveryForm(django.forms.ModelForm):
    class Meta:
        model = TestDeliveryVariant
        fields = ('email',)


class TestDeliveryProvider(DeliveryProvider):
    unique_id = 'test'

    def __init__(self, delivery_types=None):
        # by default this is one type delivery provider
        self.types = delivery_types or (('pidgin', 'pidgin'),)

    def __unicode__(self):
        return _("Test delivery")

    def enum_types(self, customer=None, delivery_group=None):
        return self.types

    def get_configuration_form(self, delivery_group, typ, data):
        instance = TestDeliveryVariant(delivery_group=delivery_group,
                                       name=typ, price=20)
        return DeliveryForm(data or None, instance=instance)

    def create_variant(self, delivery_group, typ, form=None):
        return form.save()
