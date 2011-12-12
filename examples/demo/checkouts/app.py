from satchless.contrib.checkout.multistep import app

from carts.app import cart_app
from orders.app import order_app
from orders.forms import BillingForm, DeliveryDetailsForm, DeliveryMethodForm

class CheckoutApp(app.MultiStepCheckoutApp):

    Cart = cart_app.Cart
    Order = order_app.Order
    billing_details_form_class = BillingForm
    delivery_details_form_class = DeliveryDetailsForm
    delivery_method_form_class = DeliveryMethodForm

checkout_app = CheckoutApp()
