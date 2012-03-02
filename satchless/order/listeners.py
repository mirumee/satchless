from satchless.cart.signals import cart_content_changed

def cart_content_changed_listener(sender, instance, **kwargs):
    for order in instance.orders.filter(status='checkout'):
        order.groups.all().delete()

def start_listening():
    cart_content_changed.connect(cart_content_changed_listener, weak=False)
