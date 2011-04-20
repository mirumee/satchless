from decimal import Decimal
from django import template

from satchless.product.models import Category

register = template.Library()

@register.filter
def get_categories(slugs):
    slugs = slugs.split(',')
    return dict((c.slug, c) for c in Category.objects.filter(slug__in=slugs))

def price_quantize(price):
    return price.quantize(Decimal('0.01'))
