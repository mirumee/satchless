from django.conf.urls.defaults import patterns, url
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST

from ..order import handler
from ..order.exceptions import EmptyCart
from ..order.signals import order_pre_confirm
from ..payment import PaymentFailure, ConfirmationFormNeeded
from ..core.app import SatchlessApp

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
        super(CheckoutApp, self).__init__(*args, **kwargs)
        assert self.Order, ('You need to subclass CheckoutApp and provide Order')
        assert self.Cart, ('You need to subclass CheckoutApp and provide Cart')

    def get_order(self, request, order_token):
        user = request.user if request.user.is_authenticated() else None
        try:
            return self.Order.objects.get(token=order_token, user=user)
        except self.Order.DoesNotExist:
            return

    def get_no_order_redirect_url(self):
        return '/'

    def redirect_order(self, order):
        if not order:
            return redirect(self.get_no_order_redirect_url())
        elif order.status == 'checkout':
            return self.redirect('checkout',
                                 order_token=order.token)
        elif order.status == 'payment-pending':
            return self.redirect('confirmation',
                                 order_token=order.token)
        return redirect('order:details', order_token=order.token)

    @method_decorator(require_POST)
    def prepare_order(self, request, cart_token):
        cart = get_object_or_404(self.Cart, token=cart_token,
                                 typ=self.cart_type)
        order_pk = request.session.get('satchless_order')
        previous_orders = self.Order.objects.filter(pk=order_pk,
                                                    cart=cart,
                                                    status='checkout')
        try:
            order = previous_orders.get()
        except self.Order.DoesNotExist:
            try:
                order = self.Order.objects.get_from_cart(cart)
            except EmptyCart:
                return redirect('cart:details')
        if request.user.is_authenticated():
            if cart.owner != request.user:
                cart.owner = request.user
                cart.save()
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
            url(r'^prepare/(?P<cart_token>\w+)/$', self.prepare_order,
                name='prepare-order'),
            url(r'^(?P<order_token>\w+)/$', self.checkout,
                name='checkout'),
            url(r'^(?P<order_token>\w+)/confirmation/$', self.confirmation,
                name='confirmation'),
            url(r'^(?P<order_token>\w+)/reactivate/$', self.reactivate_order,
                name='reactivate-order'),
        )


