from django.conf.urls.defaults import patterns, url
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST

from ..cart.models import Cart
from ..order import handler
from ..order.exceptions import EmptyCart
from ..order.models import Order
from ..order.signals import order_pre_confirm
from ..payment import PaymentFailure, ConfirmationFormNeeded
from ..core.app import SatchlessApp

class CheckoutApp(SatchlessApp):
    app_name = 'checkout'
    namespace = 'checkout'
    cart_model = Cart
    cart_type = 'cart'
    order_model = Order
    confirmation_templates = [
        'satchless/checkout/confirmation.html',
    ]

    def get_order(self, request, order_token):
        user = request.user if request.user.is_authenticated() else None
        try:
            return self.order_model.objects.get(token=order_token, user=user)
        except self.order_model.DoesNotExist:
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
    def prepare_order(self, request):
        cart = self.cart_model.objects.get_or_create_from_request(request,
                                                                  self.cart_type)
        order_pk = request.session.get('satchless_order')
        previous_orders = self.order_model.objects.filter(pk=order_pk,
                                                          cart=cart,
                                                          status='checkout')
        try:
            order = previous_orders.get()
        except self.order_model.DoesNotExist:
            try:
                order = self.order_model.objects.get_from_cart(cart)
            except EmptyCart:
                return redirect('cart:details')
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

        order_pre_confirm.send(sender=self.order_model, instance=order,
                               request=request)
        try:
            handler.payment_queue.confirm(order=order)
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