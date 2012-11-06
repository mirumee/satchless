from satchless.order import forms
from satchless.contrib.checkout.multistep import app

from carts.app import cart_app
from orders.app import order_app
from django.forms.models import modelform_factory


class CheckoutApp(app.MultiStepCheckoutApp):

    Order = order_app.Order

    BillingForm = modelform_factory(order_app.Order,
                                    forms.BillingForm)
    ShippingForm = modelform_factory(order_app.DeliveryGroup,
                                     form=forms.ShippingForm,
                                     fields=forms.ShippingForm._meta.fields)
    DeliveryMethodForm = modelform_factory(order_app.DeliveryGroup,
                                           form=forms.DeliveryMethodForm,
                                           fields=forms.DeliveryMethodForm._meta.fields)

checkout_app = CheckoutApp(cart_app)
