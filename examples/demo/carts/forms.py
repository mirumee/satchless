# -*- coding:utf-8 -*-
from django import forms

class AddToCartForm(forms.Form):
    quantity = forms.DecimalField(initial=1)

    def __init__(self, cart, wishlist, data=None, *args, **kwargs):
        self.wishlist = wishlist
        self.cart = cart
        super(AddToCartForm, self).__init__(data=data, *args, **kwargs)
        if self._wishlist_request():
            del self.fields['quantity']

    def _wishlist_request(self):
        return 'wishlist' in self.data if self.data else False

    def clean(self):
        data = super(AddToCartForm, self).clean()
        # skip quantity validation when adding into wishlist
        if not self._wishlist_request():
            qty = data['quantity']
            add_result = self.cart.add_item(self.get_variant(), qty, dry_run=True)
            if add_result.quantity_delta < qty:
                raise forms.ValidationError(add_result.reason)
        return data

    def save(self):
        if self._wishlist_request():
            return self.wishlist.add_item(self.get_variant(), 1)
        else:
            return self.cart.add_item(self.get_variant(), self.cleaned_data['quantity'])


class WishlistAddToCartItemForm(forms.Form):
    request_marker = forms.CharField(widget=forms.HiddenInput(),
                                     required=False)

    def __init__(self, cart, *args, **kwargs):
        self.cart = cart
        super(WishlistAddToCartItemForm, self).__init__(*args, **kwargs)
        self.is_bound = (self.is_bound and
                         self.add_prefix('request_marker') in self.data)
        if not self.is_bound:
            self.data = None

    def clean(self):
        data = super(WishlistAddToCartItemForm, self).clean()
        add_result = self.cart.add_item(self.get_variant(), 1, dry_run=True)
        if add_result.quantity_delta < 1:
            raise forms.ValidationError(add_result.reason)
        return data

    def save(self):
        return self.cart.add_item(self.get_variant(), 1)
