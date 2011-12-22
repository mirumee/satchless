from django.db import models

from orders.app import order_app
from satchless.contrib.payment.django_payments_provider.models import DjangoPaymentsPayment

class Payment(DjangoPaymentsPayment):

    order = models.OneToOneField(order_app.Order,
                                 related_name='paymentvariant')
