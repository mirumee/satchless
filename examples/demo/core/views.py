# -*- coding:utf-8 -*-
from django.contrib import messages
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _

from orders.app import order_app

def home_page(request):
    messages.success(request, _(u'<strong>Welcome!</strong> This is a demo shop built on Satchless. Enjoy!'))
    return TemplateResponse(request, 'core/home_page.html')

def thank_you_page(request, order_token):
    order = order_app.get_order(request, order_token)
    if not order.status in ('payment-failed', 'payment-complete', 'delivery'):
        return redirect(order_app.reverse('details',
                                          args=(order.token,)))
    if order.status == 'payment-failed':
        return redirect('payment-failed', order_token=order.token)

    return TemplateResponse(request, 'satchless/checkout/thank_you.html', {
        'order': order,
    })

def payment_failed(request, order_token):
    order = order_app.get_order(request, order_token)
    if order.status != 'payment-failed':
        return redirect(order)
    return TemplateResponse(request, 'satchless/checkout/payment_failed.html', {
        'order': order,
    })

