# -*- coding:utf-8 -*-
import decimal

from django import forms
from django.forms.models import inlineformset_factory
from django.utils.translation import ugettext as _

import satchless.cart.forms
import satchless.cart.models

MAX_VARIANT_QUANTITY = 10

class AddToCartForm(satchless.cart.forms.AddToCartForm):
    quantity = forms.TypedChoiceField(choices=([(v,v) for v in range(MAX_VARIANT_QUANTITY)]),
                                      coerce=lambda v: decimal.Decimal(v), initial=1)

class EditCartItemForm(satchless.cart.forms.EditCartItemForm):
    quantity = forms.TypedChoiceField(choices=([(v,v) for v in range(MAX_VARIANT_QUANTITY)]),
                                      coerce=lambda v: decimal.Decimal(v), initial=1)

CartItemFormSet = inlineformset_factory(satchless.cart.models.Cart, satchless.cart.models.CartItem,
                                        form=EditCartItemForm, fields=('quantity',), extra=0)
