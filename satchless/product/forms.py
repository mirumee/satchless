from django import forms

from .signals import variant_formclass_for_product

class BaseVariantForm(forms.Form):
    product = None

    def __init__(self, *args, **kwargs):
        self.product = kwargs.pop('product')
        variant = kwargs.pop('variant', None)
        super(BaseVariantForm, self).__init__(*args, **kwargs)
        # If we have a Variant, fill initials with data from the instance
        if variant:
            for field in variant._meta.fields:
                name = field.name
                if not self.fields.has_key(name):
                    continue
                self.fields[name].initial = getattr(variant, name)


def variant_form_for_product(product):
    formclass = []
    variant_formclass_for_product.send(sender=type(product),
                                       instance=product,
                                       formclass=formclass)
    if len(formclass) > 1:
        raise ValueError("Multiple form classes returned for %s: %s." %
                         (product._meta.object_name, formclass))
    elif not len(formclass):
        raise ValueError("No form class returned for %s." %
                         (product._meta.object_name, ))
    return formclass[0]
