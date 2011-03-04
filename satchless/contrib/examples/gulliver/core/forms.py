# -*- coding:utf-8 -*-
import decimal

from django import forms
from django.utils.translation import ugettext as _

import satchless.cart.forms

class AddToCartForm(satchless.cart.forms.AddToCartForm):
    quantity = forms.TypedChoiceField(choices=([(v,v) for v in [1,2,3,4,5]]),
                                      coerce=lambda v: decimal.Decimal(v), initial=1)

