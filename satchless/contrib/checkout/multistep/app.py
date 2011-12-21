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

    BillingForm = None
    DeliveryMethodForm = None
    DeliveryMethodFormSet = None
    ShippingForm = None
    ShippingFormSet = None

    def __init__(self, *args, **kwargs):
        super(MultiStepCheckoutApp, self).__init__(self, *args, **kwargs)
        assert ((self.ShippingForm or self.ShippingFormSet) and
                (self.DeliveryMethodFormSet or self.DeliveryMethodForm) and
                self.BillingForm), ('You need to subclass MultiStepCheckoutApp '
                                    'and provide BillingForm, DeliveryMethodForm, '
                                    'ShippingForm')
        self.ShippingFormSet = (
            self.ShippingFormSet or
            modelformset_factory(self.ShippingForm._meta.model,
                                 form=self.ShippingForm,
                                 extra=0))
        self.DeliveryMethodFormSet = (
            self.DeliveryMethodFormSet or
            modelformset_factory(self.DeliveryMethodForm._meta.model,
                                 form=self.DeliveryMethodForm,
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
        billing_form = self.BillingForm(data=request.POST or None,
                                        instance=order)
        groups = order.groups.all()
        shipping_formset = self.ShippingFormSet(data=request.POST or None,
                                                queryset=groups)
        if all([billing_form.is_valid(),
                shipping_formset.is_valid()]):
            order = billing_form.save()
            shipping_formset.save()
            return self.redirect('delivery-method', order_token=order.token)
        return TemplateResponse(request, self.checkout_templates, {
            'billing_form': billing_form,
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
        delivery_method_formset = self.DeliveryMethodFormSet(data=request.POST or None,
                                                             queryset=delivery_groups)
        if delivery_method_formset.is_valid():
            delivery_method_formset.save()
            return self.redirect('payment-method', order_token=order.token)
        return TemplateResponse(request, self.delivery_method_templates, {
            'delivery_method_formset': delivery_method_formset,
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
        delivery_group_forms = []
        for group in groups:
            delivery_type = group.delivery_type
            form = handler.delivery_queue.get_configuration_form(group,
                                                                 request.POST or None)
            delivery_group_forms.append((group, delivery_type, form))
        delivery_forms = [form for group, typ, form in delivery_group_forms]
        if all(form.is_valid() if form else True
               for form in delivery_forms):
            for group, typ, form in delivery_group_forms:
                handler.delivery_queue.save(group, form)
            return self.redirect('payment-method', order_token=order.token)
        return TemplateResponse(request, self.delivery_details_templates, {
            'delivery_group_forms': delivery_group_forms,
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


