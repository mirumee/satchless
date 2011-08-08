.. _intro-products:

=========================================
Creating a Product Catalog with Satchless
=========================================

Once you have :ref:`installed Satchless<intro-installation>`, you will want to
start adding your products to the database. Satchless comes with a number of
modules to help you get started. This page is a tutorial on how to create
products, add variants to each product, and add taxes and pricing. It is a
broad overview, so if you need specific details, refer to the individual
module's documentation.

Product Review
--------------

Before diving in and writing product models, you must first understand how
items in your store are structured. Satchless uses three distinct to structure
a store. These are covered in more detail in the :ref:`product overview
<product-overview>` section. For our purposes, let's review them: **category**,
**product**, and **variant**. 

    * A **Category** is the grouping of your products and/or a grouping of
      other categories. In order for an item to be shown in the store, it must
      have a category. This is because the product lists in Satchless are based
      on the category view.

    * A **Product** is the representation of a product in the storefront. This
      is the model that is referred to when building an individual product page,
      but is not what is purchased by the customer. Instead, the customer will
      purchase:

    * The **Variant** of the product. Products can come in many shapes and
      sizes, but each variation is typically its own item. For example, a shoe
      may have a particular product model, but different variations in size and
      colour. Because each variation of the shoe is a separate item, satchless
      variant models are also where the SKU (Stock-keeping unit) of the item is
      stored.

Shoes and Tacos
---------------

The concepts of **categories**, **products**, and **variants**, are fine and
dandy, but are somewhat unintuitive without a concrete example. Let's consider
two different kinds of stores: a shoestore and a taco stand. In the example of
a shoe store, each variant is a completely separate item. A size 12 black shoe
is different from a size 6 tan shoe, even if the shoe is the same product. On
the other hand, a taco's variants do not matter as much; each taco's variant is
the same price. For this tutorial, we'll assume that each taco has three
variants: "regular", "large", and "supreme".

This documentation, as well as the :ref:`shop tutorial <intro-simpleshop>` are
based on the example store ``examples.sombraro``, so feel free to have a gander
at those if necessary.

Your Custom Product Models
--------------------------

After :ref:`installing Satchless<intro-installation>`, go to your application
directory and run::

    python manage.py startapp tacos

This will create a new folder ``tacos`` with the files ``__init__.py``,
``models.py``, ``views.py``, and ``tests.py``. This folder is a python module
containing everything you need to start writing your custom product models. Be
sure to add it to the ``settings.py`` file like so::

    INSTALLED_APPS = (
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.admin',
        'mptt',
        'satchless.product',
        'satchless.image',

        # You may skip the following ones when running just a product catalog:
        'satchless.contact',
        'satchless.cart',
        'satchless.pricing',
        'satchless.order',

        # Insert your product module name here
        'tacos',
        'satchless.contrib.productset',
    )

Now open ``models.py`` with your favourite editor and define your products,
categories, and variants. Because this is a taco stand, we'll assume that each
product has three size variants. We do not make toppings into separate
variants, this is because the toppings and customizations of each taco are
handled in the checkout step of the purchase [#]_. For a product like shoes,
each item is a distinct variant by virtue of the fact that each item is a
distinct purchasable variation of the main product. Tacos only have size
variants to worry about.

Here's how the models are implemented in the demo (``demo.sombraro``)::

        from django.db import models

        # satchless abstract classes
        from satcheless.image.models import Image # uses settings.py to determine sizes
        from satchless.product.models import ProductAbstract, Variant, Product

        # for localization support
        from django.utils.translation import ugettext as _

        class ProductImage(Image):
            product = models.ForeignKey(Product, related_name="images")
            caption = models.CharField(_("Caption"), max_length=128, blank=True)
            order = models.PositiveIntegerField(blank=True)

            class Meta:
                ordering = ('order',)

            def __unicode__(self):
                return os.path.basename(self.image.name)

            def save(self, *args, **kwargs):
                """
                automatically adds an ordering to the saved image
                """
                if self.order is None:
                    self.order = self.product.images.aggregate(max_order=models.Max("order"))['max_order'] or 0
                return super(ProductImage, self).save(*args, **kwargs)

        class Product(ProductAbstract):
            """
            Here we define the base model for our store's products. This is where
            additional meta-data (such as creation date and model) can be added.
            """
            main_image = models.ForeignKey(ProductImage, null=True, blank=True,
                on_delete=models.SET_NULL,
                help_text=_("Main product image (first image by default)"))

            class Meta:
                abstract = True

        class Taco(Product):
            """
            FINALLY! The money-maker. The taco.
            """
            class Meta:
                verbose_name = _("Taco")
                verbose_name_plural = _("Tacos")
            # wasn't that easy? :)
            # As I said, the important logic is mostly stored in the variants

        class TacoVariant(Variant):
            """
            Assuming these tacos are served in the US, we'll want to make sure to not
            add a "small" variant. Instead, we'll assume that no one wants a small
            taco.
            """
            product = models.ForeignKey(Taco, related_name="variants")
            SIZE_CHOICES = (
                ('regular', _("Regular")),
                ('large', _("Large")),
                ('supreme', _("Supreme")),
            )
            size = models.CharField(max_length=32, choices=SIZE_CHOICES)
            class Meta:
                abstract = True

        # SIGNALS
        """
            Signals are used for assigning the main image to the product. If you'd
            like, you can also put them in a file called "listeners.py" as long as you
            add the following to this apps' __init__.py file:
                import listeners
        """

        def assign_main_image(sender, instance, **kwargs):
            if not kwargs.get('raw', False) and instance.product.main_image == None \
                    and instance.product.images.exists():
                instance.product.main_image = instance.product.images.all()[0]
                instance.product.save()
        models.signals.post_save.connect(assign_main_image, sender=ProductImage)

        def assign_new_main_image(sender, instance, **kwargs):
            try:
                if instance.product.main_image == instance and instance.product.images.exists():
                    instance.product.main_image = instance.product.images.all()[0]
                    instance.product.save()
            except Product.DoesNotExist:
                pass
        models.signals.post_delete.connect(assign_new_main_image, sender=ProductImage)


.. [#] This sort of adjustment to the order is undocumented and perhaps
   unimplemented at the time of this writing, but will be implemented in the
   near future.

Your Custom Form
----------------

Now that your models are defined, your going to want to present them to the
customer somehow. However, supposing that not all of your tacos are offered in
all variations you're going to want to write a form which only uses available
variants. Here's how we handle the form in this store::

        from django import forms
        from satchless.forms.widgets import DecimalInput
        from satchless.product.forms import BaseVariantForm
        from models import Taco, TacoVariant

        class ProductPriceForm(forms.ModelForm):
            class Meta:
                widgets = {
                    'price': DecimalInput(min_decimal_places=2),
                }

        class TacoVariantForm(BaseVariantForm):
            size = forms.CharField(
                    max_length=6,
                    widget=forms.Select(choices=[]))

            def __init__(self, *args, **kwargs):
                super(TacoVariantForm, self).__init__(*args, **kwargs)
                used_sizes = self.product.variants.values_list('size', flat=True).distinct()
                size_choices = [(k, v)
                                for k, v in TacoVariant.SIZE_CHOICES
                                if k in used_sizes]
                self.fields['size'].widget.choices = size_choices

            def _get_variant_queryset(self):
                return TacoVariant.objects.filter(
                    product=self.product,
                    size=self.cleaned_data['size'],
                )

            def clean(self):
                if not self._get_variant_queryset().exists():
                    raise forms.ValidationError("We are sorry but we don't carry this"
                                                "size of taco")
                return self.cleaned_data

            def get_variant(self):
                return self._get_variant_queryset().get()


The Taco Admin
--------------

Now that we know how we want to display Taco sizes to the user, we can start
writing our ``admin.py`` so we can add Taco Products using the django admin
interface. This code is based on the ``example.demo`` store and is modified for our taco stand. Refer to the ``example.demo`` source for further examples of using inlines.

Our taco stand admin.py looks like::

        # -*- coding:utf-8 -*-
        from django.conf import settings
        from django.contrib import admin
        import django.db.models

        from django.db.models.query import EmptyQuerySet

        from satchless.contrib.pricing import simpleqty
        import satchless.product.models
        import satchless.product.admin
        import satchless.category.models
        import satchless.category.admin
        import sale.models

        from . import models
        from . import widgets
        from .forms import ProductPriceForm

        class ImageInline(admin.TabularInline):
            formfield_overrides = {
                django.db.models.ImageField: { 'widget': widgets.AdminImageWidget },
            }

        class ProductImageInline(ImageInline):
            extra = 4
            max_num = 4
            model = models.ProductImage
            sortable_field_name = "order"

        class ProductForm(satchless.product.admin.ProductForm):
            def __init__(self, *args, **kwargs):
                super(ProductForm, self).__init__(*args, **kwargs)
                if self.instance.id:
                    self.fields['main_image'].queryset =\
                        (models.ProductImage.objects.filter(product=self.instance))
                else:
                    self.fields['main_image'].queryset =\
                        EmptyQuerySet(model=models.ProductImage)

        class ProductAdmin(satchless.product.admin.ProductAdmin):
            form = ProductForm

        class ProductImageInline(ImageInline):
            extra = 4
            man_num = 4
            model = models.ProductImage
            sortable_field_name = "order"

        class PriceInline(admin.TabularInline):
            model = simpleqty.models.ProductPrice
            form = ProductPriceForm

        class DiscountInline(admin.TabularInline):
            model = sale.models.DiscountGroup.products.through
            max_num = 1

        class CategoryImageInline(ImageInline):
            model = models.CategoryImage

        class CategoryWithImageAdmin(satchless.category.admin.CategoryAdmin):
            inlines = [CategoryImageInline]

        class TacoVariantInline(admin.TabularInline):
            model = models.TacoVariant

        class TacoAdmin(ProductAdmin):
            inlines = [ProductImageInline, TacoVariantInline, PriceInline,
                    DiscountInline]

        admin.site.unregister(satchless.category.models.Category)
        admin.site.register(models.Category, CategoryWithImageAdmin)

        admin.site.register(models.Taco, TacoAdmin)


Going Forward
-------------

Once you've written your custom product models and added a few products, you're
going to want to :ref:`set up your storefront <intro-simpleshop>` for
customers to browse, search, and purchase your product.

TODO:

    * Admin documentation for adding products (with screenshots).
    * Document "toppings" and similar free customizations.

