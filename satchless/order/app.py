from django.conf.urls.defaults import patterns, url
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from ..core.app import SatchlessApp

from . import models
from . import handler

class OrderApp(SatchlessApp):
    app_name = 'satchless-order'
    order_model = models.Order
    order_templates = [
        'satchless/order/view.html',
        'satchless/order/my_orders.html',
    ]

    def my_orders(request):
        orders = self.order_model.objects.filter(user=request.user)
        return TemplateResponse(request, 'satchless/order/my_orders.html', {
            'orders': orders,
        })

    def view_order(self, request, order_token):
        if request.user.is_authenticated():
            orders = self.order_model.objects.filter(user=request.user)
        else:
            orders = self.order_model.objects.filter(user=None)
        order = self.get_order(request, token=order_token)
        return TemplateResponse(request, 'satchless/order/view.html', {
            'order': order,
        })

    def get_template_names(self, order, **kwargs):
        return self.order_templates

    def get_order(self, request, order_token):
        order = get_object_or_404(self.order_model, token=order_token)
        return order

    def get_context_data(self, request, **kwargs):
        return kwargs

    def get_urls(self, prefix=None):
        prefix = prefix or self.app_name
        return patterns('',
            url(r'^my-orders/$', self.my_orders, name='satchless-order-my-orders'),
            url(r'^(?P<order_token>[0-9a-zA-Z]+)/$', self.view_order, name='satchless-order-view'),
        )

order_app = OrderApp()