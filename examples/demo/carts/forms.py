# -*- coding:utf-8 -*-
from django import forms

class AddToCartBaseForm(forms.Form):
    def __init__(self, data=None, *args, **kwargs):
        typ = kwargs.pop('typ')
        # validate only when correct button was pressed
        if data and not typ in data:
            data = None
        self.cart = kwargs.pop('cart', None)
        super(AddToCartBaseForm, self).__init__(data=data, *args, **kwargs)


class AddToCartForm(AddToCartBaseForm):
    quantity = forms.DecimalField(initial=1)

    def clean(self):
        data = super(AddToCartForm, self).clean()
        if 'quantity' in data:
            qty = data['quantity']
            add_result = self.cart.add_item(self.get_variant(), qty, dry_run=True)
            if add_result.quantity_delta < qty:
                raise forms.ValidationError(add_result.reason)
        return data

    def save(self):
        return self.cart.add_item(self.get_variant(), self.cleaned_data['quantity'])


class AddToWishlistForm(AddToCartBaseForm):
    def save(self):
        return self.cart.add_item(self.get_variant(), 1)

