# -*- coding:utf-8 -*-
from django.utils.translation import ugettext_lazy as _

import satchless.delivery
import satchless.payment
import satchless.payment.models

class TestDeliveryVariant(satchless.delivery.models.DeliveryVariant):
    pass

class TestDeliveryProvider(satchless.delivery.DeliveryProvider):
    name = _("Test delivery")

    def __unicode__(self):
        return unicode(self.name)

    def enum_types(self, customer=None, delivery_group=None):
        return (('pidgin', 'pidgin'),)

    def get_formclass(self, delivery_group, typ):
        return None

    def create_variant(self, delivery_group, typ, form=None):
        variant = TestDeliveryVariant()
        variant.delivery_group = delivery_group
        variant.name = typ
        variant.price = '20'
        variant.save()
        return variant

class TestPaymentProvider(satchless.payment.PaymentProvider):
    def enum_types(self, order=None, customer=None):
        return (('gold', 'gold'),)

    def get_configuration_formclass(self, order, typ):
        return None

    def create_variant(self, order, typ, form):
        payment_variant = TestPaymentVariant.objects \
                                            .create(order=order, price=0, name='test')
        return payment_variant

    def confirm(self, order):
        pass

class TestPaymentVariant(satchless.payment.models.PaymentVariant):
    pass
