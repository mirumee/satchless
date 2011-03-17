from django.dispatch import receiver

from satchless.product.signals import variant_formclass_for_product
from satchless.product.forms import NonConfigurableVariantForm

from . import forms
from . import models

@receiver(variant_formclass_for_product, sender=models.Cardigan)
def get_cardiganvariant_formclass(sender, instance, formclass, **kwargs):
    formclass.append(forms.CardiganVariantForm)

@receiver(variant_formclass_for_product, sender=models.Dress)
def get_dressvariant_formclass(sender, instance, formclass, **kwargs):
    formclass.append(forms.DressVariantForm)

@receiver(variant_formclass_for_product, sender=models.Hat)
def get_hatvariant_formclass(sender, instance, formclass, **kwargs):
    formclass.append(NonConfigurableVariantForm)

@receiver(variant_formclass_for_product, sender=models.Jacket)
def get_jacketvariant_formclass(sender, instance, formclass, **kwargs):
    formclass.append(forms.JacketVariantForm)

@receiver(variant_formclass_for_product, sender=models.Shirt)
def get_shirtvariant_formclass(sender, instance, formclass, **kwargs):
    formclass.append(forms.ShirtVariantForm)

@receiver(variant_formclass_for_product, sender=models.TShirt)
def get_tshirtvariant_formclass(sender, instance, formclass, **kwargs):
    formclass.append(forms.TShirtVariantForm)

@receiver(variant_formclass_for_product, sender=models.Trousers)
def get_trousersvariant_formclass(sender, instance, formclass, **kwargs):
    formclass.append(forms.TrousersVariantForm)
