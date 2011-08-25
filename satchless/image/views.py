from django.http import HttpResponseNotFound
from django.shortcuts import get_object_or_404, redirect

from . import IMAGE_SIZES
from . import models


def thumbnail(request, image_id, size):
    image = get_object_or_404(models.Image, id=image_id)
    if not size in IMAGE_SIZES:
        return HttpResponseNotFound()    

    return redirect(models.Thumbnail.objects.get_or_create_at_size(image.id, size))
