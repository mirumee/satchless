from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from . import models

@login_required
def my_orders(request):
    orders = models.Order.objects.filter(user=request.user)
    return TemplateResponse(request, 'satchless/order/my_orders.html', {
        'orders': orders,
    })

def view(request, order_token):
    if request.user.is_authenticated():
        orders = models.Order.objects.filter(user=request.user)
    else:
        orders = models.Order.objects.filter(user=None)
    order = get_object_or_404(orders, token=order_token)
    return TemplateResponse(request, 'satchless/order/view.html', {
        'order': order,
    })
