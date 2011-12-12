from django.db import models

from orders.app import order_app

class Payment(models.Model):

    order = models.ForeignKey(order_app.Order)
