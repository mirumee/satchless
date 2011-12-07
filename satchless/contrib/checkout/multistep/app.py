# -*- coding: utf-8 -*-
import logging
from django.conf.urls.defaults import patterns, url
from django.template.response import TemplateResponse

from ....checkout import app
from ....order import forms
from ....order import handler
from ....delivery import forms as delivery_forms
from ....delivery import models as delivery_models

class MultiStepCheckoutApp(app.CheckoutApp):
    checkout_templates = [
        'satchless/checkout/checkout.html'
    ]
    delivery_method_templates = [
        'satchless/checkout/delivery_method.html'
    ]
    billing_details_templates = [
        'satchless/checkout/billing_details.html'
    ]
    payment_choice_templates = [
        'satchless/checkout/payment_choice.html'
    ]
    payment_details_templates = [
        'satchless/checkout/payment_details.html'
    ]
    
    shipping_details_model = delivery_models.PhysicalShippingDetails
    
    def checkout(self, request, order_token,
                 shipping_formset_class=delivery_forms.PhysicalShippingFormset):
        """
        Checkout step 1
        If there are any shipping details needed, user will be asked for them.
        Otherwise we redirect to step 2.
        """
        order = self.get_order(request, order_token)
        if not order or order.status != 'checkout':
            return self.redirect_order(order)

        details = self.shipping_details_model.objects.filter(delivery_group__order=order)
        logging.critical('checkout1: %s', details)
        if not details.exists():
            return self.redirect('billing-details',
                                 order_token=order.token)
        
        shipping_formset = shipping_formset_class(data=request.POST or None,
                                                  queryset=details)
        
        if request.method == 'POST':
            if shipping_formset.is_valid():
                shipping_formset.save()
                return self.redirect('delivery-method',
                                 order_token=order.token)
        return TemplateResponse(request, self.checkout_templates, {
            'shipping_formset': shipping_formset,
            'order': order,
        })

    def delivery_method(self, request, order_token,
                        delivery_formset_class=forms.DeliveryMethodFormset):
        order = self.get_order(request, order_token)
        if not order or order.status != 'checkout':
            return self.redirect_order(order)
        
        delivery_formset = delivery_formset_class(data=request.POST or None,
                                                  queryset=order.groups.filter(shipping__isnull=False))
        
        if request.method == 'POST':
            if delivery_formset.is_valid():
                delivery_formset.save()
                return self.redirect('billing-details',
                                 order_token=order.token)
        return TemplateResponse(request, self.delivery_method_templates, {
            'delivery_formset': delivery_formset,
            'order': order,
        })
    
    def billing_details(self, request, order_token, billing_form_class=forms.BillingForm):
        """
        Checkout step 2
        User chooses delivery method for each of the groups, supplies details
        for that delivery method if required, and supplies billing address.
        """
        order = self.get_order(request, order_token)
        if not order or order.status != 'checkout':
            return self.redirect_order(order)
        
        billing_form = billing_form_class(data=request.POST or None, instance=order)

        groups = order.groups.all()
        delivery_group_forms = forms.get_delivery_details_forms_for_groups(order.groups.all(),
                                                                           request.POST)
        groups_with_forms = filter(lambda gf: gf[2], delivery_group_forms)
        logging.critical('checkout2: %s', groups_with_forms)
        
        
        if request.method == 'POST':
            are_valid = billing_form.is_valid()
            for group, typ, form in delivery_group_forms:
                are_valid = are_valid and form.is_valid()
            if are_valid:
                order = billing_form.save()
                for group, typ, form in delivery_group_forms:
                    handler.delivery_queue.create_variant(group, form)
                return self.redirect('payment-choice', order_token=order.token)
        return TemplateResponse(request, self.billing_details_templates, {
            'delivery_group_forms': groups_with_forms,
            'billing_form': billing_form,
            'order': order,
        })

    def payment_choice(self, request, order_token):
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
        return TemplateResponse(request, self.payment_choice_templates, {
            'order': order,
            'payment_form': payment_form,
        })

    def payment_details(self, request, order_token):
        """
        Checkout step 4
        If any payment details are needed, user will be asked for them. Otherwise
        we redirect to  final confirmation.
        """
        order = self.get_order(request, order_token)
        if not order or order.status != 'checkout':
            return self.redirect_order(order)
        if not order.payment_type:
            return self.redirect('payment-choice', order_token=order.token)
        form = forms.get_payment_details_form(order, request.POST)
        def proceed(order, form):
            variant = handler.payment_queue.create_variant(order, form)
            order.payment_variant = variant
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
            url(r'^(?P<order_token>\w+)/billing-details/$',
                self.billing_details, name='billing-details'),
            url(r'^(?P<order_token>\w+)/payment-choice/$',
                self.payment_choice, name='payment-choice'),
            url(r'^(?P<order_token>\w+)/payment-details/$',
                self.payment_details, name='payment-details'),
        )

checkout_app = MultiStepCheckoutApp()
