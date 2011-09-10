from django import forms
import inspect

from . import models

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


class FormRegistry(object):
    product_handlers = None

    def __init__(self):
        self.product_handlers = {}

    def register(self, product_class, form_class):
        assert(issubclass(product_class, models.Product))
        assert(issubclass(form_class, BaseVariantForm))
        self.product_handlers[product_class] = form_class

    def get_handler(self, product_class):
        classes = inspect.getmro(product_class)
        for c in classes:
            if c in self.product_handlers:
                return self.product_handlers[c]
        raise ValueError('No form class returned for %s. Make sure that your'
                         ' forms module is loaded.' % (product_class, ))


registry = FormRegistry()

def variant_form_for_product(product_class, registry=registry):
    def decorate(form_class):
        registry.register(product_class, form_class)
        return form_class
    return decorate
