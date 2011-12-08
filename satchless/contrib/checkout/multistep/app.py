# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url
from django.forms.models import modelformset_factory
from django.template.response import TemplateResponse

from ....checkout import app
from ....order import forms
from ....order import handler

class MultiStepCheckoutApp(app.CheckoutApp):
    checkout_templates = [
        'satchless/checkout/checkout.html'
    ]
    delivery_method_templates = [
        'satchless/checkout/delivery_method.html'
    ]
    delivery_details_templates = [
        'satchless/checkout/delivery_details.html'
    ]
    payment_method_templates = [
        'satchless/checkout/payment_method.html'
    ]
    payment_details_templates = [
        'satchless/checkout/payment_details.html'
    ]

    billing_details_form_class = forms.BillingForm
    billing_details_formset_class = None
    delivery_details_form_class = forms.DeliveryDetailsForm
    delivery_details_formset_class = None
    delivery_method_form_class = forms.DeliveryMethodForm
    delivery_method_formset_class = None
    shipping_details_class = None

    def __init__(self, *args, **kwargs):
        super(MultiStepCheckoutApp, self).__init__(self, *args, **kwargs)
        self.billing_details_formset_class = (
            self.billing_details_formset_class or
            modelformset_factory(self.billing_details_form_class._meta.model,
                                 form=self.billing_details_form_class,
                                 extra=0))
        self.delivery_details_formset_class = (
            self.delivery_details_formset_class or
            modelformset_factory(self.delivery_details_form_class._meta.model,
                                 form=self.delivery_details_form_class,
                                 extra=0))
        self.delivery_method_formset_class = (
            self.delivery_method_formset_class or
            modelformset_factory(self.delivery_method_form_class._meta.model,
                                 form=self.delivery_method_form_class,
                                 extra=0))

    def checkout(self, request, order_token):
        """
        Checkout step 1
        If there are any shipping details needed, user will be asked for them.
        Otherwise we redirect to step 2.
        """
        order = self.get_order(request, order_token)
        if not order or order.status != 'checkout':
            return self.redirect_order(order)
        billing_form = self.billing_details_form_class(data=request.POST or None,
                                                       instance=order)
        groups = order.groups.filter(require_shipping_address=True)
        shipping_formset = self.delivery_details_formset_class(data=request.POST or None,
                                                               queryset=groups)
        if all([billing_form.is_valid(),
                shipping_formset.is_valid()]):
            order = billing_form.save()
            shipping_formset.save()
            return self.redirect('delivery-method', order_token=order.token)
        return TemplateResponse(request, self.checkout_templates, {
            'shipping_formset': shipping_formset,
            'order': order,
        })

    def delivery_method(self, request, order_token):
        """
        Checkout step 2
        User chooses delivery method for each of the groups.
        """
        order = self.get_order(request, order_token)
        if not order or order.status != 'checkout':
            return self.redirect_order(order)
        delivery_groups = order.groups.all()
        delivery_formset = self.delivery_method_formset_class(data=request.POST or None,
                                                              queryset=delivery_groups)
        if delivery_formset.is_valid():
            delivery_formset.save()
            return self.redirect('payment-method', order_token=order.token)
        return TemplateResponse(request, self.delivery_method_templates, {
            'delivery_formset': delivery_formset,
            'order': order,
        })

    def delivery_details(self, request, order_token):
        """
        Checkout step 2½
        User supplies further delivery details if needed.
        """
        order = self.get_order(request, order_token)
        groups = order.groups.all()
        if not all([group.delivery_type for group in groups]):
            return self.redirect('delivery-method', order_token=order.token)
        delivery_group_data = forms.get_delivery_details_forms_for_groups(
            groups, request.POST or None)
        delivery_forms = [form for group, typ, form in delivery_group_data]
        if all(form.is_valid() if form else True
               for form in delivery_forms):
            for group, typ, form in delivery_group_data:
                handler.delivery_queue.save(group, form)
            return self.redirect('payment-method', order_token=order.token)
        return TemplateResponse(request, self.delivery_details_templates, {
            'delivery_group_forms': delivery_group_data,
            'order': order,
        })

    def payment_method(self, request, order_token):
        """
        Checkout step 3
        User will choose the payment method.
        """
        order = self.get_order(request, order_token)
        if not order or order.status != 'checkout':
            return self.redirect_order(order)
        payment_form = forms.PaymentMethodForm(data=request.POST or None,
                                               instance=order)
        if request.method == 'POST':
            if payment_form.is_valid():
                payment_form.save()
                return self.redirect('payment-details', order_token=order.token)
        return TemplateResponse(request, self.payment_method_templates, {
            'order': order,
            'payment_form': payment_form,
        })

    def payment_details(self, request, order_token):
        """
        Checkout step 3½
        If any payment details are needed, user will be asked for them. Otherwise
        we redirect to  final confirmation.
        """
        order = self.get_order(request, order_token)
        if not order or order.status != 'checkout':
            return self.redirect_order(order)
        if not order.payment_type:
            return self.redirect('payment-method', order_token=order.token)
        form = forms.get_payment_details_form(order, request.POST)
        def proceed(order, form):
            handler.payment_queue.save(order, form=form)
            order.set_status('payment-pending')
            return self.redirect('confirmation', order_token=order.token)
        if form:
            if request.method == 'POST':
                if form.is_valid():
                    return proceed(order, form)
            return TemplateResponse(request, self.payment_details_templates, {
                'form': form,
                'order': order,
            })
        return proceed(order, form)

    def get_urls(self):
        return super(MultiStepCheckoutApp, self).get_urls() + patterns('',
            url(r'^(?P<order_token>\w+)/delivery-method/$',
                self.delivery_method, name='delivery-method'),
            url(r'^(?P<order_token>\w+)/delivery-details/$',
                self.delivery_details, name='delivery-details'),
            url(r'^(?P<order_token>\w+)/payment-method/$',
                self.payment_method, name='payment-method'),
            url(r'^(?P<order_token>\w+)/payment-details/$',
                self.payment_details, name='payment-details'),
        )