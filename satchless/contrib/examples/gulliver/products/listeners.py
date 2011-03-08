from django.dispatch import receiver

from satchless.product.signals import variant_formclass_for_product
from satchless.product.forms import NonConfigurableVariantForm

from . import forms
from . import models

@receiver(variant_formclass_for_product, sender=models.Cardigan)
def get_variantformclass(sender, instance, formclass, **kwargs):
    formclass.append(forms.CardiganVariantForm)

@receiver(variant_formclass_for_product, sender=models.Dress)
def get_variantformclass(sender, instance, formclass, **kwargs):
    formclass.append(forms.DressVariantForm)

@receiver(variant_formclass_for_product, sender=models.Hat)
def get_variantformclass(sender, instance, formclass, **kwargs):
    formclass.append(NonConfigurableVariantForm)

@receiver(variant_formclass_for_product, sender=models.Jacket)
def get_variantformclass(sender, instance, formclass, **kwargs):
    formclass.append(forms.JacketVariantForm)

@receiver(variant_formclass_for_product, sender=models.Shirt)
def get_variantformclass(sender, instance, formclass, **kwargs):
    formclass.append(forms.ShirtVariantForm)

@receiver(variant_formclass_for_product, sender=models.TShirt)
def get_variantformclass(sender, instance, formclass, **kwargs):
    formclass.append(forms.TShirtVariantForm)

@receiver(variant_formclass_for_product, sender=models.Trousers)
def get_variantformclass(sender, instance, formclass, **kwargs):
    formclass.append(forms.TrousersVariantForm)
