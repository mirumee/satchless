# -*- coding: utf-8 -*-
from django import template

register = template.Library()

@register.filter
def product_url(product, category=None):
    return product.get_absolute_url(category=category)
