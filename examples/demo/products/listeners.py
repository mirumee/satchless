from satchless.product.signals import variant_formclass_for_product

from . import forms
from . import models

def get_cardiganvariant_formclass(sender, instance, formclass, **kwargs):
    formclass.append(forms.CardiganVariantForm)

def get_dressvariant_formclass(sender, instance, formclass, **kwargs):
    formclass.append(forms.DressVariantForm)

def get_hatvariant_formclass(sender, instance, formclass, **kwargs):
    formclass.append(forms.HatVariantForm)

def get_jacketvariant_formclass(sender, instance, formclass, **kwargs):
    formclass.append(forms.JacketVariantForm)

def get_shirtvariant_formclass(sender, instance, formclass, **kwargs):
    formclass.append(forms.ShirtVariantForm)

def get_tshirtvariant_formclass(sender, instance, formclass, **kwargs):
    formclass.append(forms.TShirtVariantForm)

def get_trousersvariant_formclass(sender, instance, formclass, **kwargs):
    formclass.append(forms.TrousersVariantForm)

def start_listening():
    variant_formclass_for_product.connect(get_cardiganvariant_formclass,
                                          sender=models.Cardigan)
    variant_formclass_for_product.connect(get_dressvariant_formclass,
                                          sender=models.Dress)
    variant_formclass_for_product.connect(get_hatvariant_formclass,
                                          sender=models.Hat)
    variant_formclass_for_product.connect(get_jacketvariant_formclass,
                                          sender=models.Jacket)
    variant_formclass_for_product.connect(get_shirtvariant_formclass,
                                          sender=models.Shirt)
    variant_formclass_for_product.connect(get_tshirtvariant_formclass,
                                          sender=models.TShirt)
    variant_formclass_for_product.connect(get_trousersvariant_formclass,
                                          sender=models.Trousers)
