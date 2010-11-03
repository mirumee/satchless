from django.conf import settings

IMAGE_SIZES = getattr(settings, 'SATCHLESS_IMAGE_SIZES', {})
