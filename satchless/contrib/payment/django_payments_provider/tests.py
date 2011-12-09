from django.db import models
from django.test import TestCase
from ....order.tests import order_app
from . import DjangoPaymentsProvider
from .models import DjangoPaymentsPayment

class TestPayment(DjangoPaymentsPayment):
    order = models.OneToOneField(order_app.Order)


class TestProvider(DjangoPaymentsProvider):
    payment_class = TestPayment


class DjangoPayments(TestCase):
    pass