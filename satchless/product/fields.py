# coding: utf-8

from django import forms

class CategoryMixin:
    def label_from_instance(self, obj):
        level = getattr(obj, obj._mptt_meta.level_attr)
        indent = max(0, level - 1) * u'│'
        if level:
            indent += u'├ '
        return u'%s%s' % (indent, unicode(obj))

class CategoryChoiceField(CategoryMixin, forms.ModelChoiceField):
    pass

class CategoryMultipleChoiceField(CategoryMixin, forms.ModelMultipleChoiceField):
    pass

