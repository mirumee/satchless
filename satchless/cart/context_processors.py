from . import models

def satchless_cart(request):
    return {'satchless_cart': (models.Cart.objects.get_or_create_from_request(request, 'cart'))}