from django.test import TestCase
from mamona.models import build_payment_model
from ....order.tests import order_app
from . import MamonaProvider

TestPayment = build_payment_model(order_app.Order, unique=True,
                                  related_name='payments')

class TestProvider(MamonaProvider):
    payment_class = TestPayment


class Mamona(TestCase):
    pass