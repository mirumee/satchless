from django.db import models
from satchless.order.models import Order, OrderManager
from carts.models import DemoCart

class DemoOrder(Order):

    cart = models.ForeignKey(DemoCart, blank=True, null=True, related_name='orders')
    objects = OrderManager()