from django import forms
from django.core import validators
from django.utils.translation import ugettext_lazy as _

from ....payment.fields import (CreditCardExpirationField,
                                      CreditCardNumberField)

CVV_VALIDATOR = validators.RegexValidator('^[0-9]{1,4}$',
                                          _('Enter a valid security number.'))

class PaymentForm(forms.ModelForm):
    cc_name = forms.CharField(label=_('Name on Credit Card'), max_length=128)
    cc_number = CreditCardNumberField(label=_('Card Number'), max_length=32,
                                      required=True)
    cc_expiration = CreditCardExpirationField(label=_('Exp. date'))
    cc_cvv2 = forms.CharField(validators=[CVV_VALIDATOR], required=False,
                              label=_('CVV2 Security Number'), max_length=4)

    class Meta:
        fields = ('cc_name', 'cc_number', 'cc_expiration', 'cc_cvv2')
