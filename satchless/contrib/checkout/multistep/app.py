# -*- coding: utf-8 -*-
from django.forms.models import modelformset_factory
from django.template.response import TemplateResponse

from ....checkout import app
from ....core.app import view
from ....order import forms

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
                self.BillingForm), (
            'You need to subclass MultiStepCheckoutApp and provide BillingForm,'
            ' DeliveryMethodForm, ShippingForm')
        self.ShippingFormSet = (
            self.ShippingFormSet or
            modelformset_factory(self.ShippingForm._meta.model,
                                 form=self.ShippingForm,
                                 extra=0))
        self.DeliveryMethodFormSet = (
            self.DeliveryMethodFormSet or
            modelformset_factory(self.DeliveryMethodForm._meta.model,
                                 formset=forms.DeliveryMethodFormSet,
                                 form=self.DeliveryMethodForm,
                                 extra=0))

    @view(r'^(?P<order_token>\w+)/$', name='checkout')
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
        delivery_groups = order.groups.filter(require_shipping_address=True)
        shipping_formset = self.ShippingFormSet(data=request.POST or None,
                                                queryset=delivery_groups)
        if all([billing_form.is_valid(),
                shipping_formset.is_valid()]):
            order = billing_form.save()
            shipping_formset.save()
            return self.redirect('delivery-method', order_token=order.token)
        context = self.get_context_data(request, billing_form=billing_form,
                                        shipping_formset=shipping_formset,
                                        order=order)
        return TemplateResponse(request, self.checkout_templates, context)

    @view(r'^(?P<order_token>\w+)/delivery-method/$', name='delivery-method')
    def delivery_method(self, request, order_token):
        """
        Checkout step 2
        User chooses delivery method for each of the groups.
        """
        order = self.get_order(request, order_token)
        if not order or order.status != 'checkout':
            return self.redirect_order(order)
        delivery_groups = order.groups.all()
        delivery_method_formset = self.DeliveryMethodFormSet(
            data=request.POST or None,
            queryset=delivery_groups,
            delivery_queue=self.delivery_queue)
        if delivery_method_formset.is_valid():
            delivery_method_formset.save()
            return self.redirect('delivery-details', order_token=order.token)
        context = self.get_context_data(
            request, order=order,
            delivery_method_formset=delivery_method_formset)
        return TemplateResponse(request, self.delivery_method_templates,
                                context)

    @view(r'^(?P<order_token>\w+)/delivery-details/$', name='delivery-details')
    def delivery_details(self, request, order_token):
        """
        Checkout step 2½
        User supplies further delivery details if needed.
        """
        order = self.get_order(request, order_token)
        delivery_groups = order.groups.all()
        if not all([group.delivery_type for group in delivery_groups]):
            return self.redirect('delivery-method', order_token=order.token)
        delivery_group_forms = self.delivery_queue.get_configuration_forms_for_groups(
            delivery_groups, request.POST or None)
        delivery_forms = [form
                          for group, delivery_type, form
                          in delivery_group_forms]
        if all(form.is_valid() if form else True
               for form in delivery_forms):
            for group, delivery_type, form in delivery_group_forms:
                self.delivery_queue.save(group, form)
            return self.redirect('payment-method', order_token=order.token)
        context = self.get_context_data(
            request, order=order, delivery_group_forms=delivery_group_forms)
        return TemplateResponse(request, self.delivery_details_templates,
                                context)

    @view(r'^(?P<order_token>\w+)/payment-method/$', name='payment-method')
    def payment_method(self, request, order_token):
        """
        Checkout step 3
        User will choose the payment method.
        """
        order = self.get_order(request, order_token)
        if not order or order.status != 'checkout':
            return self.redirect_order(order)
        payment_form = forms.PaymentMethodForm(data=request.POST or None,
                                               instance=order,
                                               payment_queue=self.payment_queue)
        if request.method == 'POST':
            if payment_form.is_valid():
                payment_form.save()
                return self.redirect('payment-details', order_token=order.token)
        context = self.get_context_data(request, order=order,
                                        payment_form=payment_form)
        return TemplateResponse(request, self.payment_method_templates, context)

    @view(r'^(?P<order_token>\w+)/payment-details/$', name='payment-details')
    def payment_details(self, request, order_token):
        """
        Checkout step 3½
        If any payment details are needed, user will be asked for them.
        Otherwise we redirect to  final confirmation.
        """
        order = self.get_order(request, order_token)
        if not order or order.status != 'checkout':
            return self.redirect_order(order)
        if not order.payment_type:
            return self.redirect('payment-method', order_token=order.token)
        form = self.payment_queue.get_configuration_form(order, request.POST)
        def proceed(order, form):
            self.payment_queue.save(order, form=form)
            order.set_status('payment-pending')
            return self.redirect('confirmation', order_token=order.token)
        if form:
            if request.method == 'POST':
                if form.is_valid():
                    return proceed(order, form)
            context = self.get_context_data(request, form=form, order=order)
            return TemplateResponse(request, self.payment_details_templates,
                                    context)
        return proceed(order, form)