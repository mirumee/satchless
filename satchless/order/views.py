# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound
from django.template.response import TemplateResponse

from . import models

@login_required
def my_orders(request):
    orders = models.Order.objects.filter(user=request.user)
    return TemplateResponse(request, 'satchless/order/my_orders.html', {
        'orders': orders,
    })

def view(request, order_pk):
    if request.user.is_authenticated():
        orders = models.Order.objects.filter(user=request.user)
    elif request.session.has_key('satchless_order'):
        # We allow anonymous users to see their latest order.
        orders = models.Order.objects.filter(pk=request.session['satchless_order'])
    else:
        return HttpResponseNotFound()
    try:
        order = orders.get(pk=order_pk)
    except models.Order.DoesNotExist:
        return HttpResponseNotFound()
    return TemplateResponse(request, 'satchless/order/view.html', {
        'order': order,
    })
