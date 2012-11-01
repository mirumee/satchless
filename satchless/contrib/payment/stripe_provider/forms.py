from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from . import models
from ....payment import PaymentFailure

import stripe


class StripeReceiptForm(forms.ModelForm):
    stripe_customer_id = forms.CharField(max_length=50, required=False,
                                         label=_('Stripe Customer ID'))
    stripe_card_id = forms.CharField(max_length=50, required=False,
                                     label=_('Stripe Card ID'))

    class Meta:
        model = models.StripeReceipt

    def clean(self):
        if (not self.cleaned_data.get('stripe_customer_id')
            and not self.cleaned_data.get('stripe_card_id')):
            raise ValidationError(_("Either a Card or a Customer is required"))
        return super(StripeReceiptForm, self).clean()

    def save(self, commit=True):
        stripe.api_key = settings.STRIPE_SECRET
        stripe_card_id = self.cleaned_data.get('stripe_card_id')
        if stripe_card_id and not self.cleaned_data.get('stripe_customer_id'):
            orderer_email = self.instance.order.user.email
            try:
                customer = stripe.Customer.create(
                    card=stripe_card_id,
                    description=orderer_email,
                    email=orderer_email
                )
                self.instance.stripe_customer_id = customer.id
            except stripe.StripeError:
                raise PaymentFailure(_("Payment denied or network error"))
        return super(StripeReceiptForm, self).save(commit)
