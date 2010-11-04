from django import forms
from django.forms.models import inlineformset_factory
from satchless.product.models import Variant
from . import models

class QuantityForm(object):
    def clean_quantity(self):
        val = self.cleaned_data['quantity']
        if val < 0:
            raise forms.ValidationError, _("Quantity cannot be negative")
        return val


class AddToCartForm(forms.Form, QuantityForm):
    """Form that adds a Variant quantity to a Cart.
    It may be replaced by more advanced one, performing some checks, e.g.
    verifying the number of items in stock."""
    variant = forms.ModelChoiceField(queryset=Variant.objects.all())
    quantity = forms.DecimalField()

    def __init__(self, cart=None, *args, **kwargs):
        self.cart = cart
        super(AddToCartForm, self).__init__(*args, **kwargs)

    def save(self):
        self.cart.add_quantity(self.cleaned_data['variant'], self.cleaned_data['quantity'])


class EditCartItemForm(forms.ModelForm, QuantityForm):
    model = models.CartItem
    fields = ('quantity',)

    def save(self, commit=True):
        """Do not call the original save() method, but use cart.set_quantity() instead."""
        self.instance.cart.set_quantity(self.instance.variant, self.cleaned_data['quantity'])

CartItemFormSet = inlineformset_factory(models.Cart, models.CartItem, form=EditCartItemForm, fields=('quantity',), extra=0)
