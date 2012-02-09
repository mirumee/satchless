# -*- coding:utf-8 -*-
from PIL import Image
import StringIO

from django.core.files.base import ContentFile
from django.test import TestCase

from . import models

class ModelsTestCase(TestCase):
    def setUp(self):
        self.hat = models.Hat.objects.create(name='top hat',
                                                 slug='top-hat',
                                                 price=10)
        self.variant = self.hat.variants.create(sku='sku', stock_level=10)

    def _create_test_image(self, size=(128, 128)):
        image = Image.new('RGB', size, 'black')
        png = StringIO.StringIO()
        image.save(png, "png")
        png.seek(0)
        f = ContentFile(content=png.read())
        f.name = "test.png"
        return f

    def test_product_main_image_is_set_on_save(self):
        main_image = models.ProductImage.objects.create(image = self._create_test_image(),
                                                        product=self.hat)
        self.assertEqual(models.Hat.objects.get(id=self.hat.id).main_image, main_image)

    def test_product_main_image_is_set_on_delete(self):
        main_image = models.ProductImage.objects.create(image = self._create_test_image(),
                                                        product=self.hat)
        additional_image = models.ProductImage.objects.create(image = self._create_test_image(),
                                                              product=self.hat)

        self.assertEqual(models.Hat.objects.get(id=self.hat.id).main_image,
                                                main_image)
        main_image.delete()
        self.assertEqual(models.Hat.objects.get(id=self.hat.id).main_image,
                                                additional_image)

    def test_product_with_images_delete(self):
        models.ProductImage.objects.create(image = self._create_test_image(),
                                           product=self.hat)
        models.ProductImage.objects.create(image = self._create_test_image(),
                                           product=self.hat)
        self.hat.delete()
