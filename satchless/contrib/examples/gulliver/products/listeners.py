from django.dispatch import receiver

from satchless.product.signals import variant_formclass_for_product

from . import forms
from . import models

@receiver(variant_formclass_for_product, sender=models.Jacket)
def get_variantformclass(sender, instance, formclass, **kwargs):
    formclass.append(forms.JacketVariantForm)

