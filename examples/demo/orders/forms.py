import satchless.order.forms

from .app import order_app

class PaymentMethodForm(satchless.order.forms.PaymentMethodForm):

    class Meta:
        model = order_app.Order


class DeliveryMethodForm(satchless.order.forms.DeliveryMethodForm):

    class Meta:
        model = order_app.DeliveryGroup


class DeliveryDetailsForm(satchless.order.forms.DeliveryDetailsForm):

    class Meta:
        model = order_app.DeliveryGroup


class BillingForm(satchless.order.forms.BillingForm):

    class Meta:
        model = order_app.Order
