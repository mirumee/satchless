from django.conf.urls.defaults import patterns, url
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator

from ..core.app import SatchlessApp

class OrderApp(SatchlessApp):

    app_name = 'order'
    namespace = 'order'
    order_class = None
    order_details_templates = [
        'satchless/order/view.html',
        'satchless/order/%(order_model)s/view.html'
    ]
    order_list_templates = [
        'satchless/order/my_orders.html',
        'satchless/order/%(order_model)s/my_orders.html'
    ]

    def __init__(self, *args, **kwargs):
        super(OrderApp, self).__init__(*args, **kwargs)
        assert self.order_class, ('You need to subclass OrderApp and provide'
                                  ' order_class')

    @method_decorator(login_required)
    def index(self, request):
        orders = self.order_class.objects.filter(user=request.user)
        context = self.get_context_data(request, orders=orders)
        format_data = {
            'order_model': self.order_class._meta.module_name
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
            orders = self.order_class.objects.filter(user=request.user)
        else:
            orders = self.order_class.objects.filter(user=None)
        order = get_object_or_404(orders, token=order_token)
        return order

    def get_urls(self, prefix=None):
        prefix = prefix or self.app_name
        return patterns('',
            url(r'^$', self.index, name='index'),
            url(r'^(?P<order_token>[0-9a-zA-Z]+)/$', self.details,
                name='details'),
        )
