from django import template

register = template.Library()

@register.filter
def product_in_category_url(product, category):
    return product.get_url(category=category)
