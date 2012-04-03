========
Products
========

.. highlightlang:: python


``ProductApp``
==============

Namespace: ``product``.

The ``ProductApp`` class lives in the ``satchless.product.app`` module and serves the purpose of displaying single products on your website.


Attributes
----------


``Product``
^^^^^^^^^^^

The class to use as a product model.


``Variant``
^^^^^^^^^^^

The class to use as a variant model.

.. warning:: You need to either subclass and set ``Product`` and ``Variant`` or use ``MagicProductApp`` described below.


Views
-----

``product:details``
^^^^^^^^^^^^^^^^^^^

Method: ``ProductApp.product_details``

URLs:
 * ``/+{product_pk}-{product_slug}/$'``

Context variables:
 * ``product``: the matched product

Takes a product PK and its slug, retrieves the product from the database, runs all product view handlers (see below) and returns a ``TemplateResponse``.


Methods
-------


``get_product_details_templates(product)``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Finds a template suitable to display a particular product.

The default always returns ``['satchless/product/view.html']``.


``register_product_view_handler(handler)``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Adds a new product view handler. See below for the description of product view handlers.


``MagicProductApp``
===================

It's a "magic" subclass of ``ProductApp`` that takes care of the creation of the ``Product`` and ``Variant`` classes.

You can use it out of the box by simply creating an instance and binding it to an URL route::

    from django.conf.urls.defaults import patterns, include, url
    from satchless.product.app import MagicProductApp

    product_app = MagicProductApp()

    urlpatterns = patterns('',
        url(r'^products/', include(product_app.urls)),
    )

.. note:: Remember, *you can never have more than one instance of the same magic app in the project*.


``CategorizedProductApp``
=========================

Namespace: ``product``.

The ``CategorizedProductApp`` class lives in the ``satchless.category.app`` module and it's a subclass of ``ProductApp`` that also handles categories.


Attributes
----------

``Category``
^^^^^^^^^^^^

The class to use as a category model.

.. warning:: You need to either subclass and set ``Category`` or use ``MagicCategorizedProductApp`` described below.


Views
-----

``product:details``
^^^^^^^^^^^^^^^^^^^

Method: ``CategorizedProductApp.product_details``

URLs:
 * ``/{category_slugs}/+{product_pk}-{product_slug}/``

Context variables:
 * ``categories``: all root-level categories
 * ``product``: the matched product
 * ``path``: a list of categories forming the breadcrumbs leading to the current product

Takes a product PK, its slug and category slugs, retrieves the matching product from the database, runs all product view handlers (see below) and returns a ``TemplateResponse``.


``product:category-details``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Method: ``CategorizedProductApp.category_details``

URLs:
 * ``/{category_slug}/``
 * ``/{parent_slugs}/{category_slug}/``

Context variables:
 * ``categories``: all root-level categories
 * ``category``: the matched category
 * ``path``: a list of categories forming the breadcrumbs leading to the current category

Takes a category slug and its parent slugs, retrieves the matching category from the database and returns a ``TemplateResponse``.


``product:category-index``
^^^^^^^^^^^^^^^^^^^^^^^^^^

Method: ``CategorizedProductApp.category_list``

URLs:
 * ``/``

Context variables:
 * ``categories``: all root-level categories

Just returns a ``TemplateResponse``.


``MagicCategorizedProductApp``
==============================

It's a "magic" subclass of ``CategorizedProductApp`` that takes care of the creation of the ``Product``, ``Variant`` and ``Category`` classes.

You can use it out of the box by simply creating an instance and binding it to an URL route::

    from django.conf.urls.defaults import patterns, include, url
    from satchless.product.app import MagicCategorizedProductApp

    product_app = MagicCategorizesProductApp()

    urlpatterns = patterns('',
        url(r'^products/', include(product_app.urls)),
    )

.. note:: Remember, *you can never have more than one instance of the same magic app in the project*.


Product view handlers
=====================

Sometimes additional actions have to be taken when a product is viewed such as calculating statistics or determining prices. For this purpose Satchless allows you to register handlers with that are called each time a product is displayed.

To register a new handler, define a function or method with the following signature::

    def my_handler(product_instances, request, extra_context):
        # to push additional data to the template, alter the extra_context
        extra_context['parrot'] = 'pining for the fjords'

Then register it with your instance of ProductApp::

    my_product_app = MyProductApp()
    my_product_app.register_product_view_handler(my_handler)