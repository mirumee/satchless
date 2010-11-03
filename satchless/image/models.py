import hashlib

from django.core.urlresolvers import reverse
from django.db import models
from . import storage

hashed_storage = storage.HashedStorage()

class Image(models.Model):
    image = models.ImageField(upload_to='image/original/',
            height_field='height', width_field='width', storage=hashed_storage)
    height = models.PositiveIntegerField(default=0, editable=False)
    width = models.PositiveIntegerField(default=0, editable=False)

    def get_by_size(self, size):
        return self.thumbnail_set.get(size=size)

    def get_absolute_url(self, size=None):
        if not size:
            return self.image.url
        try:
            return self.get_by_size(size).image.url
        except Thumbnail.DoesNotExist:
            return reverse('satchless-image-thumbnail', args=(self.id, size))

class Thumbnail(models.Model):
    original = models.ForeignKey(Image)
    image = models.ImageField(upload_to='image/thumbnail/',
            height_field='height', width_field='width', storage=hashed_storage)
    size = models.CharField(max_length=100)
    height = models.PositiveIntegerField(default=0, editable=False)
    width = models.PositiveIntegerField(default=0, editable=False)

    class Meta:
        unique_together = ('image', 'size')
