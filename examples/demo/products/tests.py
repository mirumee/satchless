# -*- coding:utf-8 -*-
from PIL import Image
import StringIO

from django.core.files.base import ContentFile
from django.test import TestCase
from prices import Price, PriceRange

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
        main_image = models.ProductImage.objects.create(
            image=self._create_test_image(), product=self.hat)
        self.assertEqual(models.Hat.objects.get(id=self.hat.id).main_image,
                         main_image)

    def test_product_main_image_is_set_on_delete(self):
        main_image = models.ProductImage.objects.create(
            image=self._create_test_image(), product=self.hat)
        additional_image = models.ProductImage.objects.create(
            image=self._create_test_image(), product=self.hat)

        self.assertEqual(models.Hat.objects.get(id=self.hat.id).main_image,
                         main_image)
        main_image.delete()
        self.assertEqual(models.Hat.objects.get(id=self.hat.id).main_image,
                         additional_image)

    def test_product_with_images_delete(self):
        models.ProductImage.objects.create(image=self._create_test_image(),
                                           product=self.hat)
        models.ProductImage.objects.create(image=self._create_test_image(),
                                           product=self.hat)
        self.hat.delete()

    def test_product_price(self):
        another_hat = models.Hat.objects.create(name='Silly Hat',
                                                slug='silly-hat',
                                                price=10)
        another_hat_simple_variant = another_hat.variants.create(
            price_offset=0, sku='silly-hat-simple')
        another_hat_offset_variant = another_hat.variants.create(
            price_offset=10, sku='silly-hat-offset')
        self.assertEqual(another_hat_simple_variant.get_price(),
                         Price(10, currency='EUR'))
        self.assertEqual(another_hat_offset_variant.get_price(),
                         Price(20, currency='EUR'))
        self.assertEqual(another_hat.get_price_range(),
                         PriceRange(Price(10, currency='EUR'),
                                    Price(20, currency='EUR')))

    def test_discounted_product_price(self):
        another_discount = models.Discount.objects.create(
            name='Flying Sale', rate=50)
        another_hat = models.Hat.objects.create(name='Silly Hat',
                                                slug='silly-hat',
                                                price=10,
                                                discount=another_discount)
        another_hat_simple_variant = another_hat.variants.create(
            price_offset=0, sku='silly-hat-simple')
        another_hat_offset_variant = another_hat.variants.create(
            price_offset=10, sku='silly-hat-offset')
        self.assertEqual(another_hat_simple_variant.get_price(),
                         Price(5, currency='EUR'))
        self.assertEqual(another_hat_offset_variant.get_price(),
                         Price(10, currency='EUR'))
        self.assertEqual(another_hat.get_price_range(),
                         PriceRange(Price(5, currency='EUR'),
                                    Price(10, currency='EUR')))
        self.assertEqual(another_hat_simple_variant.get_price(discount=False),
                         Price(10, currency='EUR'))
        self.assertEqual(another_hat_offset_variant.get_price(discount=False),
                         Price(20, currency='EUR'))
        self.assertEqual(another_hat.get_price_range(discount=False),
                         PriceRange(Price(10, currency='EUR'),
                                    Price(20, currency='EUR')))

    def test_qty_overrides(self):
        another_hat = models.Hat.objects.create(name='Silly Hat',
                                                slug='silly-hat',
                                                price=10)
        another_hat_variant = another_hat.variants.create(
            price_offset=0, sku='silly-hat-simple')
        models.PriceQtyOverride.objects.create(
            product=another_hat, min_qty=5, price=8)
        self.assertEqual(another_hat_variant.get_price(),
                         Price(10, currency='EUR'))
        self.assertEqual(another_hat_variant.get_price(quantity=10),
                         Price(8, currency='EUR'))
