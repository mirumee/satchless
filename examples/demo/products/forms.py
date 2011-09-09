# -*- coding:utf-8 -*-
from django import forms

from satchless.product.forms import BaseVariantForm, variant_form_for_product

from . import models

def _get_existing_variants_choices(queryset, field_names):
    existing_choices = {}
    existing_variants = queryset.values_list(*field_names)

    if existing_variants:
        for index, existing_field_choices in enumerate(zip(*existing_variants)):
            field_name = field_names[index]
            original_choices = queryset.model._meta.get_field(field_name).choices
            existing_choices[field_names[index]] = filter(lambda choice: choice[0] in existing_field_choices,
                                                         original_choices)
    else:
        for field_name in field_names:
            existing_choices[field_name] = []
    return existing_choices

class VariantWithSizeAndColorForm(BaseVariantForm):
    color = forms.CharField(max_length=10,
            widget=forms.Select(choices=models.ColoredVariant.COLOR_CHOICES))

    def __init__(self, *args, **kwargs):
        super(VariantWithSizeAndColorForm, self).__init__(*args, **kwargs)
        existing_choices = _get_existing_variants_choices(self.product.variants.all(),
                                                          ('color', 'size'))
        for field_name, choices in existing_choices.items():
            self.fields[field_name].widget.choices = choices

    def _get_variant_queryset(self):
        return self.product.variants.filter(color=self.cleaned_data['color'],
                                            size=self.cleaned_data['size'])

    def clean(self):
        if not self._get_variant_queryset().exists():
            raise forms.ValidationError("Variant does not exist")
        return self.cleaned_data

    def get_variant(self):
        return self._get_variant_queryset().get()

@variant_form_for_product(models.Cardigan)
class CardiganVariantForm(VariantWithSizeAndColorForm):
    size = forms.CharField(max_length=10,
            widget=forms.Select(choices=models.CardiganVariant.SIZE_CHOICES))

@variant_form_for_product(models.Dress)
class DressVariantForm(VariantWithSizeAndColorForm):
    size = forms.CharField(max_length=10,
            widget=forms.Select(choices=models.DressVariant.SIZE_CHOICES))

@variant_form_for_product(models.Hat)
class HatVariantForm(BaseVariantForm):
    def get_variant(self):
        return self.product.variants.get()

@variant_form_for_product(models.Jacket)
class JacketVariantForm(VariantWithSizeAndColorForm):
    size = forms.CharField(max_length=10,
            widget=forms.Select(choices=models.JacketVariant.SIZE_CHOICES))

@variant_form_for_product(models.Shirt)
class ShirtVariantForm(VariantWithSizeAndColorForm):
    size = forms.CharField(max_length=10,
            widget=forms.Select(choices=models.ShirtVariant.SIZE_CHOICES))

@variant_form_for_product(models.TShirt)
class TShirtVariantForm(VariantWithSizeAndColorForm):
    size = forms.CharField(max_length=10,
            widget=forms.Select(choices=models.TShirtVariant.SIZE_CHOICES))

@variant_form_for_product(models.Trousers)
class TrousersVariantForm(VariantWithSizeAndColorForm):
    size = forms.CharField(max_length=10,
            widget=forms.Select(choices=models.TrousersVariant.SIZE_CHOICES))
