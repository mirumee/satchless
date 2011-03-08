# -*- coding:utf-8 -*-
from django import forms
from django.utils.translation import ugettext as _

from satchless.product.forms import BaseVariantForm, NonConfigurableVariantForm

from . import models

def _get_existing_variants_choices(queryset, field_names):
    existing_choices = {}
    existing_variants = queryset.values_list(*field_names)

    for index, existing_field_choices in enumerate(zip(*existing_variants)):
        field_name = field_names[index]
        original_choices = queryset.model._meta.get_field(field_name).choices
        existing_choices[field_names[index]] = filter(lambda choice: choice[0] in existing_field_choices,
                                                     original_choices)
    return existing_choices

class ColoredVariantForm(BaseVariantForm):
    color = forms.CharField(max_length=10,
            widget=forms.Select(choices=models.ColoredVariant.COLOR_CHOICES))

    def _get_variant_queryset(self):
        raise NotImplementedError()

    def clean(self):
        if not self._get_variant_queryset().exists():
            raise forms.ValidationError("Variant does not exist")
        return self.cleaned_data

    def get_variant(self):
        return self._get_variant_queryset().get()

class TShirtVariantForm(ColoredVariantForm):
    size = forms.CharField(max_length=10,
            widget=forms.Select(choices=models.TShirtVariant.SIZE_CHOICES))
    def _get_variant_queryset(self):
        return models.TShirtVariant.objects.filter(
                product=self.product,
                color=self.cleaned_data['color'],
                size=self.cleaned_data['size'])

class ShirtVariantForm(ColoredVariantForm):
    size = forms.CharField(max_length=10,
            widget=forms.Select(choices=models.ShirtVariant.SIZE_CHOICES))

    def __init__(self, *args, **kwargs):
        super(ShirtVariantForm, self).__init__(*args, **kwargs)
        existing_choices = _get_existing_variants_choices(
                models.ShirtVariant.objects.all(), ('color', 'size'))
        for field_name, choices in existing_choices.items():
            self.fields[field_name].widget.choices = choices

    def _get_variant_queryset(self):
        return models.ShirtVariant.objects.filter(
                product=self.product,
                color=self.cleaned_data['color'],
                size=self.cleaned_data['size'])

class CardiganVariantForm(ColoredVariantForm):
    size = forms.CharField(max_length=10,
            widget=forms.Select(choices=models.CardiganVariant.SIZE_CHOICES))

    def __init__(self, *args, **kwargs):
        super(CardiganVariantForm, self).__init__(*args, **kwargs)
        existing_choices = _get_existing_variants_choices(
                models.CardiganVariant.objects.all(), ('color', 'size'))
        for field_name, choices in existing_choices.items():
            self.fields[field_name].widget.choices = choices

    def _get_variant_queryset(self):
        return models.CardiganVariant.objects.filter(
                product=self.product,
                color=self.cleaned_data['color'],
                size=self.cleaned_data['size'])

class JacketVariantForm(ColoredVariantForm):
    size = forms.CharField(max_length=10,
            widget=forms.Select(choices=models.JacketVariant.SIZE_CHOICES))
    def __init__(self, *args, **kwargs):
        super(JacketVariantForm, self).__init__(*args, **kwargs)
        existing_choices = _get_existing_variants_choices(
                models.JacketVariant.objects.all(), ('color', 'size'))
        for field_name, choices in existing_choices.items():
            self.fields[field_name].widget.choices = choices

    def _get_variant_queryset(self):
        return models.JacketVariant.objects.filter(
                product=self.product,
                color=self.cleaned_data['color'],
                size=self.cleaned_data['size'])

class TrousersVariantForm(ColoredVariantForm):
    size = forms.CharField(max_length=10,
            widget=forms.Select(choices=models.TrousersVariant.SIZE_CHOICES))

    def __init__(self, *args, **kwargs):
        super(TrousersVariantForm, self).__init__(*args, **kwargs)
        existing_choices = _get_existing_variants_choices(
                models.TrousersVariant.objects.all(), ('color', 'size'))
        for field_name, choices in existing_choices.items():
            self.fields[field_name].widget.choices = choices

    def _get_variant_queryset(self):
        return models.TrousersVariant.objects.filter(
                product=self.product,
                color=self.cleaned_data['color'],
                size=self.cleaned_data['size'])

class DressVariantForm(ColoredVariantForm):
    size = forms.CharField(max_length=10,
            widget=forms.Select(choices=models.DressVariant.SIZE_CHOICES))

    def __init__(self, *args, **kwargs):
        super(DressVariantForm, self).__init__(*args, **kwargs)
        existing_choices = _get_existing_variants_choices(
                models.DressVariant.objects.all(), ('color', 'size'))
        for field_name, choices in existing_choices.items():
            self.fields[field_name].widget.choices = choices

    def _get_variant_queryset(self):
        return models.DressVariant.objects.filter(
                product=self.product,
                color=self.cleaned_data['color'],
                size=self.cleaned_data['size'])
