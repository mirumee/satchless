# coding: utf-8

from django import forms

class CategoryMixin:
    def label_from_instance(self, obj):
        level = getattr(obj, obj._mptt_meta.level_attr)
        indent = max(0, level - 1) * u'│'
        if obj.parent:
            last = obj.parent.get_children().order_by('-rght')[0]
            if last == obj and not obj.get_children().exists():
                indent += u'└ '
            else:
                indent += u'├ '
        return u'%s%s' % (indent, unicode(obj))

class CategoryChoiceField(CategoryMixin, forms.ModelChoiceField):
    pass

class CategoryMultipleChoiceField(CategoryMixin, forms.ModelMultipleChoiceField):
    pass

