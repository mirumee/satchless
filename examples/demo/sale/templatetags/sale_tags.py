from django.utils.datastructures import SortedDict
from django.conf import settings
from django.core.urlresolvers import reverse
from django import template

from satchless.product.models import Product
from satchless.category.models import Category

from .. import query

register = template.Library()

@register.filter
def category_in_sale_url(category):
    path = list(category.get_ancestors()) + [category]
    path = [c.slug for c in path]
    category_slugs = '/'.join(path)
    return reverse('sale', args=(category_slugs,))

@register.filter
def subcategories_in_sale(category):
    ProductCategory = Product.categories.through
    discounted_products = ProductCategory.objects.filter(product__discount__isnull=False) \
                                                        .values_list('category_id', flat=True)
    all_subcategories = Category.objects.filter(lft__gt=category.lft, rght__lt=category.rght,
                                                tree_id=category.tree_id)
    subcategories = query.add_filtered_related_count(Category.tree, all_subcategories,
                                                  discounted_products, 'category', 'products_count',
                                                  cumulative=True)
    subcategories = filter(lambda cat: cat.products_count, subcategories)
    return subcategories

@register.filter
def product_in_category_tree_url(product, category=None):
    if not category:
        return product.get_url()

    category = Category.objects.filter(products=product, lft__gte=category.lft,
                                       rght__lte=category.rght)[0]
    return product.get_url(category=category)

