# -*- coding:utf-8 -*-
from django import forms
from django.forms.models import inlineformset_factory

import satchless.cart.forms
import satchless.cart.models

class AddToCartForm(forms.Form):
    quantity = forms.DecimalField(initial=1)

    def __init__(self, data=None, *args, **kwargs):
        typ = kwargs.pop('typ')
        # validate only when correct button was pressed
        if data and not typ in data:
            data = None
        self.cart = kwargs.pop('cart', None)
        super(AddToCartForm, self).__init__(data=data, *args, **kwargs)

    def clean(self):
        data = super(AddToCartForm, self).clean()
        qty = data['quantity']
        add_result = self.cart.add_quantity(self.get_variant(), qty, dry_run=True)
        if add_result.quantity_delta < qty:
            raise forms.ValidationError(add_result.reason)
        return data

    def save(self):
        return self.cart.add_quantity(self.get_variant(), self.cleaned_data['quantity'])

class AddToWishlistForm(AddToCartForm):
    def save(self):
        return self.cart.add_quantity(self.get_variant(), 1)

