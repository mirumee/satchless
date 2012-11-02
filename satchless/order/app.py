from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator

from ..core.app import SatchlessApp, view
from ..util.models import construct
from . import models


class OrderApp(SatchlessApp):

    app_name = 'order'
    namespace = 'order'
    Order = None
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
        assert self.Order, ('You need to subclass OrderApp and provide'
                            ' Order')

    @view(r'^$', name='index')
    @method_decorator(login_required)
    def index(self, request):
        orders = self.Order.objects.filter(user=request.user)
        context = self.get_context_data(request, orders=orders)
        format_data = {
            'order_model': self.Order._meta.module_name
        }
        templates = [p % format_data for p in self.order_list_templates]
        return TemplateResponse(request, templates, context)

    @view(r'^(?P<order_token>[0-9a-zA-Z]+)/$', name='details')
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
            orders = self.Order.objects.filter(user=request.user)
        else:
            orders = self.Order.objects.filter(user=None)
        order = get_object_or_404(orders, token=order_token)
        return order


class MagicOrderApp(OrderApp):

    DeliveryGroup = None
    OrderedItem = None

    def __init__(self, cart_app, **kwargs):
        self.Order = (self.Order or
                      self.construct_order_class(cart_app.Cart))
        self.DeliveryGroup = (self.DeliveryGroup or
                              self.construct_delivery_group_class(self.Order))

        self.OrderedItem = (
            self.OrderedItem or
            self.construct_ordered_item_class(self.DeliveryGroup,
                                              cart_app.product_app.Variant))
        super(MagicOrderApp, self).__init__(**kwargs)

    def construct_order_class(self, cart_class):
        class Order(construct(models.Order, cart=cart_class)):
            pass

        return Order

    def construct_delivery_group_class(self, order_class):
        class DeliveryGroup(construct(models.DeliveryGroup,
                                      order=order_class)):
            pass

        return DeliveryGroup

    def construct_ordered_item_class(self, delivery_group_class, variant_class):
        class OrderedItem(construct(models.OrderedItem,
                                    delivery_group=delivery_group_class,
                                    variant=variant_class)):
            pass

        return OrderedItem
