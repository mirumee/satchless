# -*- coding:utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_images.models import Image
import satchless.category.models


class Category(satchless.category.models.Category):

    class Meta:
        verbose_name = _("category")
        verbose_name_plural = _("categories")


class CategoryImage(Image):

    category = models.OneToOneField(Category, related_name='image')

    class Meta:
        verbose_name_plural = _("Category image")
