from satchless.cart.signals import cart_content_changed

def cart_content_changed_listener(sender, instance=None, **kwargs):
    if instance.is_empty():
        instance.orders.filter(status='checkout').delete()
    else:
        for order in instance.orders.filter(status='checkout'):
            order.__class__.objects.get_from_cart(instance, instance=order)

def start_listening():
    cart_content_changed.connect(cart_content_changed_listener, weak=False)
