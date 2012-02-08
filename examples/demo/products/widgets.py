# -*- coding:utf-8 -*-
import os

from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
import django.forms

class AdminImageWidget(django.forms.FileInput):
    def render(self, name, value, attrs=None):
        output = ['<p class="file-upload">']
        if value and hasattr(value, 'instance'):
            image = value.instance
            thumbnail_url = reverse('image-thumbnail', args=(image.id, 'admin'))
            output.append(u'<a class="image" rel="gallery" href="%s"><img src="%s" alt="" /></a><br />' % (
                    image.image.url, thumbnail_url))
        if value and hasattr(value, "url"):
            output.append('%s <a target="_blank" href="%s">%s</a> <br />%s ' % \
                (_('Currently:'), value.url, os.path.basename(value.name), _('Change:')))
        output.append(super(AdminImageWidget, self).render(name, value, attrs))
        output.append('</p>')
        return mark_safe(u''.join(output))
