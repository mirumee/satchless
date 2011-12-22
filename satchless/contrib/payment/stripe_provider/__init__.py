from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from ....payment import PaymentProvider, PaymentFailure, PaymentType
from . import forms
from . import models

import stripe
import datetime

class StripeProvider(PaymentProvider):
    form_class = forms.StripeReceiptForm

    def enum_types(self, order=None, customer=None):
        yield PaymentType(provider=self, typ='stripe', name='Stripe.com')

    def get_configuration_form(self, order, typ, data):
        instance = models.StripeReceipt(order=order, price=0)
        return self.form_class(data or None, instance=instance)

    def save(self, order, form, typ=None):
        order.payment_price = 0
        order.payment_type_name = 'Stripe.com'
        order.payment_type_description = ''
        if form.is_valid():
            form.save()
        else:
            raise PaymentFailure(_("Could not create Stripe Variant"))

    def confirm(self, order, typ=None):
        v = order.paymentvariant.get_subtype_instance()
        stripe.api_key = settings.STRIPE_SECRET_KEY
        amount = int(order.get_total().net * 100) # in cents, Stripe only does USD
        try:
            if v.stripe_card_id and not v.stripe_customer_id:
                customer = stripe.Customer.create(
                    card=v.stripe_card_id,
                    description=order.user.email,
                    email=order.user.email
                )
                customer_id = customer.id
            elif v.stripe_customer_id:
                customer_id = v.stripe_customer_id
            else:
                raise PaymentFailure(_("Requires either a card or customer."))

            charge = stripe.Charge.create(
                amount=amount,
                currency="usd",
                customer=customer_id,
                description=order.user.email,
            )
        except stripe.StripeError:
            raise PaymentFailure(_("Payment denied or network error"))

        data = {}
        try:
            data = charge.__dict__
            data['token'] = data['id']
            data.update(data['card'].__dict__)
            data['card_type'] = data['type']
            # Stripe response has creation time as unix timestamp
            data['created'] = \
                datetime.datetime.fromtimestamp(int(data['created']))
        except Exception:
            pass
        finally:
            receipt_form = forms.StripeReceiptForm(data)
            if receipt_form.is_valid():
                v.receipt = receipt_form.save()
                v.save()