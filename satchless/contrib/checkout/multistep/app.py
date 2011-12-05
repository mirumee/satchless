# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url
from django.template.response import TemplateResponse

from ....checkout import app
from ....order import forms
from ....order import handler

class MultiStepCheckoutApp(app.CheckoutApp):
    checkout_templates = [
        'satchless/checkout/checkout.html'
    ]
    delivery_details_templates = [
        'satchless/checkout/delivery_details.html'
    ]
    payment_choice_templates = [
        'satchless/checkout/payment_choice.html'
    ]
    payment_details_templates = [
        'satchless/checkout/payment_details.html'
    ]

    def checkout(self, request, order_token, billing_form_class=forms.BillingForm,
                 delivery_formset_class=forms.DeliveryMethodFormset):
        """
        Checkout step 1
        The order is split into delivery groups. User chooses delivery method
        for each of the groups.
        """
        order = self.get_order(request, order_token)
        billing_form = billing_form_class(data=request.POST or None, instance=order)
        delivery_formset = delivery_formset_class(
                data=request.POST or None, queryset=order.groups.all())
        if request.method == 'POST':
            if all([billing_form.is_valid(), delivery_formset.is_valid()]):
                order = billing_form.save()
                delivery_formset.save()
                return self.redirect('delivery-details',
                                     order_token=order.token)
        return TemplateResponse(request, self.checkout_templates, {
            'billing_form': billing_form,
            'delivery_formset': delivery_formset,
            'order': order,
        })

    def delivery_details(self, request, order_token):
        """
        Checkout step 1½
        If there are any delivery details needed (e.g. the shipping address),
        user will be asked for them. Otherwise we redirect to step 2.
        """
        order = self.get_order(request, order_token)
        if not order or order.status != 'checkout':
            return self.redirect_order(order)
        groups = order.groups.all()
        if filter(lambda g: not g.delivery_type, groups):
            return self.redirect('checkout', order_token=order.token)
        delivery_group_forms = forms.get_delivery_details_forms_for_groups(order.groups.all(),
                                                                           request.POST)
        groups_with_forms = filter(lambda gf: gf[2], delivery_group_forms)
        if len(groups_with_forms) == 0:
            # all forms are None, no details needed
            return self.redirect('payment-choice', order_token=order.token)
        if request.method == 'POST':
            are_valid = True
            for group, typ, form in delivery_group_forms:
                are_valid = are_valid and form.is_valid()
            if are_valid:
                for group, typ, form in delivery_group_forms:
                    handler.delivery_queue.create_variant(group, form)
                return self.redirect('payment-choice', order_token=order.token)
        return TemplateResponse(request, self.delivery_details_templates, {
            'delivery_group_forms': groups_with_forms,
            'order': order,
        })

    def payment_choice(self, request, order_token):
        """
        Checkout step 2
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
        Checkout step 2½
        If any payment details are needed, user will be asked for them. Otherwise
        we redirect to step 3.
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
            url(r'^(?P<order_token>\w+)/delivery-details/$',
                self.delivery_details, name='delivery-details'),
            url(r'^(?P<order_token>\w+)/payment-choice/$', self.payment_choice,
                name='payment-choice'),
            url(r'^(?P<order_token>\w+)/payment-details/$',
                self.payment_details, name='payment-details'),
        )

checkout_app = MultiStepCheckoutApp()
