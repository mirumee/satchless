from django import template

from ..models import Thumbnail

register = template.Library()

@register.filter
def at_size(image, size):
    return image.get_absolute_url(size=size)

@register.filter
def img_at_size(image, size):
    return Thumbnail.objects.get_or_create_at_size(image.id,size)
