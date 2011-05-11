from satchless.cart.signals import cart_content_changed

def init():
    from .models import Order
    def cart_content_changed_listener(sender, instance=None, **kwargs):
        for order in instance.orders.filter(status='checkout'):
            Order.objects.get_from_cart(instance, instance=order)
    cart_content_changed.connect(cart_content_changed_listener, weak=False)
