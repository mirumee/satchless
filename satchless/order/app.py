from django.conf.urls.defaults import patterns, url
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from ..core.app import SatchlessApp
from . import models

class OrderApp(SatchlessApp):
    app_name = 'order'
    namespace = 'order'
    order_model = models.Order
    order_details_templates = [
        'satchless/order/view.html',
        'satchless/order/%(order_model)s/view.html'
    ]
    order_list_templates = [
        'satchless/order/my_orders.html',
        'satchless/order/%(order_model)s/my_orders.html'
    ]

    def index(self, request):
        orders = self.order_model.objects.filter(user=request.user)
        context = self.get_context_data(request, orders=orders)
        format_data = {
            'order_model': self.order_model._meta.module_name
        }
        templates = [p % format_data for p in self.order_list_templates]
        return TemplateResponse(request, templates, context)

    def details(self, request, order_token):
        order = self.get_order(request, order_token=order_token)
        context = self.get_context_data(request, order=order)
        format_data = {
            'order_model': order._meta.module_name
        }
        templates = [p % format_data for p in self.order_details_templates]
        return TemplateResponse(request, templates, context)

    def get_order(self, request, order_token):
        if request.user.is_authenticated():
            orders = self.order_model.objects.filter(user=request.user)
        else:
            orders = self.order_model.objects.filter(user=None)
        order = get_object_or_404(orders, token=order_token)
        return order

    def get_urls(self, prefix=None):
        prefix = prefix or self.app_name
        return patterns('',
            url(r'^$', self.index, name='index'),
            url(r'^(?P<order_token>[0-9a-zA-Z]+)/$', self.details,
                name='details'),
        )

order_app = OrderApp()
