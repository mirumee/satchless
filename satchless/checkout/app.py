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
    app_name = 'satchless-checkout'
    cart_model = Cart
    order_model = Order
    no_order_redirect_url = '/'

    def get_order(self, request, order_token):
        user = request.user if request.user.is_authenticated() else None
        try:
            return self.order_model.objects.get(token=order_token, user=user)
        except self.order_model.DoesNotExist:
            return

    def get_no_order_redirect_url(self):
        return self.no_order_redirect_url

    def redirect_order(self, order):
        if not order:
            return redirect(self.get_no_order_redirect_url())
        elif order.status == 'checkout':
            return redirect(self.checkout,
                            order_token=order.token)
        elif order.status == 'payment-pending':
            return redirect(self.confirmation,
                            order_token=order.token)
        return redirect('satchless-order-view',
                        order_token=order.token)

    @method_decorator(require_POST)
    def prepare_order(self, request, typ):
        cart = self.cart_model.objects.get_or_create_from_request(request, typ)
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
                return redirect('satchless-cart-view', typ=typ)
        request.session['satchless_order'] = order.pk
        return redirect(self.checkout, order_token=order.token)

    @method_decorator(require_POST)
    def reactivate_order(self, request, order_token):
        order = self.get_order(request, order_token)
        if not order or order.status != 'payment-failed':
            return self.redirect_order(order)
        order.set_status('checkout')
        return redirect('satchless-checkout', order_token=order.token)

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
            return TemplateResponse(request, 'satchless/checkout/confirmation.html', {
                'formdata': e,
                'order': order,
            })
        except PaymentFailure:
            order.set_status('payment-failed')
        else:
            order.set_status('payment-complete')
        return redirect('satchless-order-view', order_token=order.token)

    def get_urls(self):
        return patterns('',
            url(r'^prepare/$', self.prepare_order, {'typ': 'satchless_cart'},
                name='%s-prepare-order' % self.app_name),
            url(r'^(?P<order_token>\w+)/$', self.checkout,
                name='%s' % self.app_name),
            url(r'^(?P<order_token>\w+)/confirmation/$', self.confirmation,
                name='%s-confirmation' % self.app_name),
            url(r'^(?P<order_token>\w+)/reactivate/$', self.reactivate_order,
                name='%s-reactivate-order' % self.app_name),
        )


