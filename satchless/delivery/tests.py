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

    def get_formclass(self, delivery_group, typ):
        return DeliveryForm

    def create_variant(self, delivery_group, typ, form=None):
        variant = TestDeliveryVariant()
        variant.delivery_group = delivery_group
        variant.name = typ
        variant.price = '20'
        variant.save()
        return variant

