from satchless.product.signals import variant_formclass_for_product
from . import forms
from . import models

def get_variantformclass(sender=None, instance=None, formclass=None, **kwargs):
    formclass.append(forms.ParrotVariantForm)

variant_formclass_for_product.connect(get_variantformclass, sender=models.Parrot)
