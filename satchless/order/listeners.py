from satchless.cart.signals import cart_content_changed

def cart_content_changed_listener(sender, instance=None, **kwargs):
    instance.orders.filter(status='checkout').delete()

cart_content_changed.connect(cart_content_changed_listener)
