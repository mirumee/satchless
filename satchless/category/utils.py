# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse

def get_product_url(product, category):
    if category:
        return reverse('satchless-category-product-details',
                       ('%s%s/' % (category.parents_slug_path(),
                                   category.slug),
                       product.slug))
    return reverse('satchless-product-details', (product.slug, product.pk))

