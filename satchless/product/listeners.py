from . import signals
from . import models
from . import forms

def get_nonconfvariant_formclass(sender=None, instance=None, formclass=[], **kwargs):
    formclass.append(forms.NonConfigurableVariantForm)

signals.variant_formclass_for_product.connect(
        get_nonconfvariant_formclass,
        sender=models.NonConfigurableVariantForm)
