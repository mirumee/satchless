from satchless.product.signals import variant_formclass_for_product
from . import models
from . import forms

def get_variant_formclass(sender=None, instance=None, formclass=[], **kwargs):
    formclass.append(forms.DummyVariantForm)

variant_formclass_for_product.connect(get_variant_formclass, sender=models.Dummy)
