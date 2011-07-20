.. _product-overview:

==================
Satchless products
==================

When it comes to products, there are three main concepts within Satchless:
category, product and variant.

    * **Category** is quite intuitive one. Satchless provides a tree
      structure for grouping your products. Actually, it can be a forest,
      which means that you can, but not have to, create a single root
      category.

      Categories in Satchless are handled by `django-mptt`_ which uses
      efficient data structure to keep and traverse the categories hierarchy.
      You may create big trees without significant performance penalty.

    * **Product** is something you want to sell. It may be a simple thing
      like *Life of Brian DVD* or more complex article, like a t-shirt, which
      comes in variety of sizes and colors.

      Products may belong to any number of categories. Each occurence of a
      product within a category has different URL, which makes it possible to
      navigate back easily and to share links to products together with a
      context of categories.

      Each product gets also it's own URL which is not related to category
      tree. This way, *orphans* are never lost.

    * **Variant**: When it comes to complex products, which are being sold
      in different sizes, colors, flavors, etc., the variant is what you
      are looking for. Varians are products with full list of parameters
      that describe it. For example, if you sell a *T-shirt with Satchless
      logo*, a variant may describe *Pink men's XL t-shirt with Satchless
      logo*.

    * **Variant selection form** shows variant options to a customer and picks
      the resulting variant using the data provided.

.. _django-mptt: http://code.google.com/p/django-mptt/

How Products and Variants work
------------------------------

The main purpose of products in Satchless is to group variants and show them
to customers and people who manage the shop on a high level. Inside, the
``Variant`` model is more important. It represents a concrete, parametrized
item. Variant is what goes to the shopping cart, and finally to order, what
is bound with prices or stock control numbers.

Every product in Satchless has a variant. Simple products may have only one.

.. note::
    Actually, the base ``satchless.product`` application does not provide
    models for managing any real products. It contains only the base classes
    to define your own models of products and their variants. Examples of code
    may be found in ``examples/`` directory.

The inside class hierarchy looks like this::

    satchless.product.models.Product
        satchless.product.models.ProductAbstract
            your_custom_products.models.CustomProduct
            your_custom_products.models.AnotherProduct

    satchless.product.models.Variant
        your_custom_products.models.CustomProductVariant
        your_custom_products.models.AnotherProductVariant

As you probably noticed, every Product subclass has its sister Variant
subclass. The convention we use in Satchless is for Variant to refer to
its Product model via ``product`` field and for Product to refer back
via ``variants`` manager.
