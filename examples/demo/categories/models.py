# -*- coding:utf-8 -*-
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _
from satchless.image.models import Image

from localeurl.models import reverse
from mothertongue.models import MothertongueModelTranslate
import satchless.category.models


class Category(satchless.category.models.Category,
               MothertongueModelTranslate):
    translated_fields = ('name', 'description', 'meta_description')
    translation_set = 'translations'

    class Meta:
        verbose_name = _("category")
        verbose_name_plural = _("categories")

    def get_url(self):
        """Uses reverse resolver, to force localeurl to add language code."""
        return reverse('satchless-product-category',
                args=(self._parents_slug_path(), self.slug))


class CategoryImage(Image):
    category = models.OneToOneField(Category, related_name='image')
    class Meta:
        verbose_name_plural = _("Category image")


class CategoryTranslation(models.Model):
    category = models.ForeignKey(Category, related_name='translations')
    language = models.CharField(max_length=5, choices=settings.LANGUAGES[1:])
    name = models.CharField(_('name'), max_length=128)
    description = models.TextField(_('description'), blank=True)
    meta_description = models.TextField(_('meta description'), blank=True,
            help_text=_("Description used by search and indexing engines"))

    class Meta(object):
        unique_together = ('category', 'language')


