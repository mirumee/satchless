# -*- coding: utf-8 -*-
from django import template

from .. import utils

register = template.Library()

@register.filter
def product_url(product, category=None):
    return utils.get_product_url(product, category)
