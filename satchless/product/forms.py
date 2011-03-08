from django import forms

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


class NonConfigurableVariantForm(BaseVariantForm):
    def get_variant(self):
        return self.product.variants.get()
