# -*- coding:utf-8 -*-
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _

from satchless.contrib.checkout.common.decorators import require_order
from satchless.order.models import Order


def home_page(request):
    messages.success(request, _(u'<strong>Welcome!</strong> This is a demo shop built on Satchless. Enjoy!'))
    return TemplateResponse(request, 'core/home_page.html')

def thank_you_page(request, order_token):
    order = get_object_or_404(Order, token=order_token)
    if not order.status in ('payment-failed', 'payment-complete', 'delivery'):
        return redirect('satchless-order-view', order_token=order.token)
    if order.status == 'payment-failed':
        return redirect('payment-failed', order_token=order.token)

    return TemplateResponse(request, 'satchless/checkout/thank_you.html', {
        'order': order,
    })

@require_order(status='payment-failed')
def payment_failed(request, order_token):
    order = get_object_or_404(Order, token=order_token)
    return TemplateResponse(request, 'satchless/checkout/payment_failed.html', {
        'order': order,
    })

