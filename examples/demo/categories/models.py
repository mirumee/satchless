# -*- coding:utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_images.models import Image
import satchless.category.models

from localeurl.models import reverse


class Category(satchless.category.models.Category):

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
