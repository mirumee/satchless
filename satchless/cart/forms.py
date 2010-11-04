from django import forms
from satchless.product.models import Variant

class AddToCartForm(forms.Form):
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
