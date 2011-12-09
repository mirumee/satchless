from django.test import TestCase
from mamona.models import build_payment_model
from ....order.tests import TestOrder
from . import MamonaProvider

TestPayment = build_payment_model(TestOrder, unique=True,
                                  related_name='payments')

class TestProvider(MamonaProvider):
    payment_class = TestPayment


class Mamona(TestCase):
    pass