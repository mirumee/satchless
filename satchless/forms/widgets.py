from decimal import Decimal
from django.forms.widgets import TextInput
from ..util import decimal_format

class DecimalInput(TextInput):
    def __init__(self, *args, **kwargs):
        self.min_decimal_places = kwargs.pop('min_decimal_places', 0)
        return super(DecimalInput, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        if isinstance(value, Decimal):
            value = decimal_format(value,
                                   min_decimal_places=self.min_decimal_places)
        return super(DecimalInput, self).render(name, value, attrs)
