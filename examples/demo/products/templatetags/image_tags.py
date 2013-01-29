from django import template
from django_images.settings import IMAGE_SIZES
from django_images.templatetags import images

register = template.Library()


@register.filter
def at_size_with_fallback(image, size):
    if not image:
        if not size in IMAGE_SIZES:
            raise ValueError("Received unknown size: %s" % size)
        w, h = IMAGE_SIZES[size]['size']
        return 'http://placekitten.com/%d/%d/' % (w, h)
    return images.at_size(image, size)
