# -*- coding:utf-8 -*-
import os

from django.conf import settings
from django.contrib.admin.widgets import AdminFileWidget
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from django.conf import settings
from django.core.urlresolvers import reverse

from satchless.image import IMAGE_SIZES

from . import models

class AdminImageWidget(AdminFileWidget):
    def render(self, name, value, attrs=None):
        output = []
        if value:
            image = value.instance
            thumbnail_url = reverse('satchless-image-thumbnail', args=(image.id, 'admin'))
            output.append(u'<a class="image" rel="gallery" href="%s"><img src="%s" alt="" /></a><br />' % (
                    image.image.url, thumbnail_url))
        output.append(super(AdminFileWidget, self).render(name, value, attrs))

        return mark_safe(u''.join(output))
