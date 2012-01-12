import hashlib
import os.path
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

from django.db import models
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.urlresolvers import reverse

from . import IMAGE_SIZES
from . import utils

def hashed_upload_to(prefix, instance, filename):
    hasher = hashlib.md5()
    for chunk in instance.image.chunks():
        hasher.update(chunk)
    hash = hasher.hexdigest()
    base, ext = os.path.splitext(filename)
    return '%(prefix)s%(first)s/%(second)s/%(hash)s/%(base)s%(ext)s' % {
        'prefix': prefix,
        'first': hash[0],
        'second': hash[1],
        'hash': hash,
        'base': base,
        'ext': ext,
    }

def image_upload_to(instance, filename, **kwargs):
    return hashed_upload_to('image/original/by-md5/', instance, filename)

class Image(models.Model):
    image = models.ImageField(upload_to=image_upload_to,
            height_field='height', width_field='width',
            max_length=255)
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


def thumbnail_upload_to(instance, filename, **kwargs):
    return hashed_upload_to('image/thumbnail/by-md5/', instance, filename)
    

class ThumbnailManager(models.Manager):
    def get_or_create_at_size(self, image_id, size):
        image = Image.objects.get(id=image_id)
        if not size in IMAGE_SIZES:
            raise ValueError("Received unknown size: %s" % size)
        try:
            thumbnail = image.get_by_size(size)
        except Thumbnail.DoesNotExist:
            img = utils.scale_and_crop(image.image, **IMAGE_SIZES[size])
            # save to memory
            buf = StringIO()
            img.save(buf, img.format, **img.info)
            # and save to storage
            original_dir, original_file = os.path.split(image.image.name)
            thumb_file = InMemoryUploadedFile(buf, "image", original_file, None, buf.tell(), None)
            thumbnail = image.thumbnail_set.create(size=size, image=thumb_file)
        return thumbnail

class Thumbnail(models.Model):
    original = models.ForeignKey(Image)
    image = models.ImageField(upload_to=thumbnail_upload_to,
            height_field='height', width_field='width')
    size = models.CharField(max_length=100)
    height = models.PositiveIntegerField(default=0, editable=False)
    width = models.PositiveIntegerField(default=0, editable=False)
    
    objects = ThumbnailManager()

    class Meta:
        unique_together = ('image', 'size')

    def get_absolute_url(self):
        return self.image.url

def original_changed(sender, instance, created, **kwargs):
    if isinstance(instance, Image):
        instance.thumbnail_set.all().delete()

models.signals.post_save.connect(original_changed)
