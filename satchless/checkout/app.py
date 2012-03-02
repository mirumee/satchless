from django.conf import settings
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST

from ..core.app import SatchlessApp, view
from ..order import handler
from ..order.signals import order_pre_confirm
from ..payment import PaymentFailure, ConfirmationFormNeeded

class CheckoutApp(SatchlessApp):
    app_name = 'checkout'
    namespace = 'checkout'
    Cart = None
    cart_type = 'cart'
    Order = None
    confirmation_templates = [
        'satchless/checkout/confirmation.html',
    ]

    def __init__(self, *args, **kwargs):
        delivery_providers = kwargs.pop('delivery_providers',
                                        getattr(settings, 'SATCHLESS_DELIVERY_PROVIDERS', []))
        self.delivery_queue = handler.DeliveryQueue(*delivery_providers)

        payment_providers = kwargs.pop('payment_providers',
                                        getattr(settings, 'SATCHLESS_PAYMENT_PROVIDERS', []))
        self.payment_queue = handler.PaymentQueue(*payment_providers)

        partitioners = kwargs.pop(
            'partitioners', getattr(settings, 'SATCHLESS_ORDER_PARTITIONERS',
                ['satchless.contrib.order.partitioner.simple.SimplePartitioner']))
        self.partitioner_queue = handler.PartitionerQueue(*partitioners)

        super(CheckoutApp, self).__init__(*args, **kwargs)
        assert self.Order, ('You need to subclass CheckoutApp and provide Order')
        assert self.Cart, ('You need to subclass CheckoutApp and provide Cart')

    def get_order(self, request, order_token):
        user = request.user if request.user.is_authenticated() else None
        try:
            return self.Order.objects.get(token=order_token, user=user)
        except self.Order.DoesNotExist:
            return

    def redirect_order(self, order):
        if not order or order.is_empty():
            return redirect('cart:details')
        elif order.status == 'checkout':
            return self.redirect('checkout',
                                 order_token=order.token)
        elif order.status == 'payment-pending':
            return self.redirect('confirmation',
                                 order_token=order.token)
        return redirect('order:details', order_token=order.token)

    def partition_cart(self, cart, order, **pricing_context):
        groups = filter(None, self.partitioner_queue.partition(cart))
        for group in groups:
            delivery_group = order.create_delivery_group(group)
            for item in group:
                delivery_group.add_item(item.variant, item.quantity,
                                        price=item.get_price(**pricing_context))
        return order

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

    @view(r'^prepare/(?P<cart_token>\w+)/$', name='prepare-order')
    @method_decorator(require_POST)
    def prepare_order(self, request, cart_token):
        cart = get_object_or_404(self.Cart, token=cart_token,
                                 typ=self.cart_type)
        if cart.is_empty():
            return redirect('cart:details')

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
            if cart.owner != request.user:
                cart.owner = request.user
                cart.save()
            if order.user != request.user:
                order.user = request.user
                order.save()

        request.session['satchless_order'] = order.pk
        return self.redirect('checkout', order_token=order.token)

    @view(r'^(?P<order_token>\w+)/reactivate/$', name='reactivate-order')
    @method_decorator(require_POST)
    def reactivate_order(self, request, order_token):
        order = self.get_order(request, order_token)
        if not order or order.status != 'payment-failed':
            return self.redirect_order(order)
        order.set_status('checkout')
        return self.redirect('checkout', order_token=order.token)

    @view(r'^(?P<order_token>\w+)/confirmation/$', name='confirmation')
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