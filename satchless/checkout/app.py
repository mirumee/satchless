from django.conf.urls.defaults import patterns, url
from django.conf import settings
from django.db.models import Q
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST

from ..order import handler
from ..order.signals import order_pre_confirm
from ..payment import PaymentFailure, ConfirmationFormNeeded
from ..core.app import SatchlessApp

class CheckoutApp(SatchlessApp):

    app_name = 'checkout'
    namespace = 'checkout'
    Order = None
    confirmation_templates = [
        'satchless/checkout/confirmation.html',
    ]

    def __init__(self, cart_app, *args, **kwargs):
        self.cart_app = cart_app
        delivery_providers = kwargs.pop('delivery_providers',
                                        getattr(settings, 'SATCHLESS_DELIVERY_PROVIDERS', []))
        self.delivery_queue = handler.DeliveryQueue(*delivery_providers)

        payment_providers = kwargs.pop('payment_providers',
                                        getattr(settings, 'SATCHLESS_PAYMENT_PROVIDERS', []))
        self.payment_queue = handler.PaymentQueue(*payment_providers)

        partitioners = kwargs.pop(
            'partitioners', getattr(settings, 'SATCHLESS_ORDER_PARTITIONERS',
                ['satchless.contrib.order.partitioner.simple.SimplePartitioner']))
        self.delivery_partitioner = handler.PartitionerQueue(*partitioners)

        super(CheckoutApp, self).__init__(*args, **kwargs)
        assert self.Order, ('You need to subclass CheckoutApp and provide Order')

    def get_order(self, request, order_token):
        user = request.user if request.user.is_authenticated() else None
        try:
            return self.Order.objects.get(token=order_token, user=user)
        except self.Order.DoesNotExist:
            return

    def redirect_order(self, order):
        if not order or order.is_empty():
            return self.cart_app.redirect('details')
        elif order.status == 'checkout':
            return self.redirect('checkout',
                                 order_token=order.token)
        elif order.status == 'payment-pending':
            return self.redirect('confirmation',
                                 order_token=order.token)
        return redirect('order:details', order_token=order.token)

    def partition_cart(self, cart, order, **pricing_context):
        groups = filter(None, self.delivery_partitioner.partition(cart))
        for group in groups:
            delivery_group = order.create_delivery_group(group)
            for cartitem in group:
                price = self.cart_app.pricing_handler.get_variant_price(
                    cartitem.variant.get_subtype_instance(), currency=cart.currency,
                    quantity=cartitem.quantity, cart=cartitem.cart,
                    cartitem=cartitem, **pricing_context)
                delivery_group.add_item(cartitem.variant, cartitem.quantity, price)

    def get_order_from_cart(self, request, cart, order=None):
        if not order:
            order = self.Order.objects.create(cart=cart, user=cart.owner,
                                              currency=cart.currency)
        elif order.is_empty():
            order.groups.all().delete()
        self.partition_cart(cart, order)
        previous_orders = self.Order.objects.filter(
            Q(cart=cart) & Q(status='checkout') & ~Q(pk=order.pk))
        previous_orders.delete()
        return order

    @method_decorator(require_POST)
    def prepare_order(self, request):
        cart = self.cart_app.get_cart_for_request(request)
        if cart.is_empty():
            return self.cart_app.redirect('details')

        order_pk = request.session.get('satchless_order')
        try:
            order = self.Order.objects.get(pk=order_pk, cart=cart,
                                           status='checkout')
        except self.Order.DoesNotExist:
            order = self.get_order_from_cart(request, cart)
        else:
            if order.is_empty():
                order = self.get_order_from_cart(request, cart, order)
        if request.user.is_authenticated():
            if order.user != request.user:
                order.user = request.user
                order.save()

        request.session['satchless_order'] = order.pk
        return self.redirect('checkout', order_token=order.token)

    @method_decorator(require_POST)
    def reactivate_order(self, request, order_token):
        order = self.get_order(request, order_token)
        if not order or order.status != 'payment-failed':
            return self.redirect_order(order)
        order.set_status('checkout')
        return self.redirect('checkout', order_token=order.token)

    def checkout(self, request, order_token):
        raise NotImplementedError()

    def confirmation(self, request, order_token):
        """
        Checkout confirmation
        The final summary, where user is asked to review and confirm the order.
        Confirmation will redirect to the payment gateway.
        """
        order = self.get_order(request, order_token)
        if not order or order.status != 'payment-pending':
            return self.redirect_order(order)

        order_pre_confirm.send(sender=self.Order, instance=order,
                               request=request)
        try:
            self.payment_queue.confirm(order=order)
        except ConfirmationFormNeeded, e:
            return TemplateResponse(request, self.confirmation_templates, {
                'formdata': e,
                'order': order,
            })
        except PaymentFailure:
            order.set_status('payment-failed')
        else:
            order.set_status('payment-complete')
        return redirect('order:details', order_token=order.token)

    def get_urls(self):
        return patterns('',
            url(r'^prepare/$', self.prepare_order,
                name='prepare-order'),
            url(r'^(?P<order_token>\w+)/$', self.checkout,
                name='checkout'),
            url(r'^(?P<order_token>\w+)/confirmation/$', self.confirmation,
                name='confirmation'),
            url(r'^(?P<order_token>\w+)/reactivate/$', self.reactivate_order,
                name='reactivate-order'),
        )


