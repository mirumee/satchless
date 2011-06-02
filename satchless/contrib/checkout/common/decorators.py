# -*- coding:utf-8 -*-
from functools import wraps

from django.shortcuts import redirect
from django.utils.decorators import available_attrs

from ....order import models

def require_order(status=None):
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            order = None
            if 'order_token' in kwargs:
                try:
                    order = models.Order.objects.get(token=kwargs['order_token'],
                                                     status=status)
                except models.Order.DoesNotExist:
                    pass
            if not order:
                return redirect('satchless-cart-view')
            elif status is not None and status != order.status:
                if order.status == 'checkout':
                    return redirect('satchless-checkout',
                                    order_token=order.token)
                elif order.status == 'payment-pending':
                    return redirect(confirmation)
                else:
                    return redirect('satchless-order-view',
                                    order_token=order.token)
            request.order = order
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

