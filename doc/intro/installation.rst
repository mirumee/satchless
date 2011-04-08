.. _intro-installation:

======================
Satchless installation
======================

Provided that you have installed all :ref:`required applications
<intro-requirements>`, installation of Satchless is quite simple
process:

The environment
---------------

First of all, include the directory containing ``satchless`` in your
``PYTHONPATH`` environment variable (or expose it to your Python interpreter
in any other way).

Create new Django project. To learn how to do it, have a look at `great
documentation`_ they provide.

Applications and settings
-------------------------

Include neccessary applications in your ``INSTALLED_APPS`` tuple in Django
``settings.py`` file. For a basic shop, the list would look like::

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

        # The following list depends on what kinds of products you want to sell:
        'satchless.contrib.products.dummy',
        'satchless.contrib.productset',
    )

Add neccessary entries to your ``urls.py`` file. The prefixes used here are
just examples and you may change them freely.::

    urlpatterns = patterns('',
        url(r'^products/', include('satchless.product.urls')),
        url(r'^contact/', include('satchless.contact.urls')),
        url(r'^image/', include('satchless.image.urls')),
        url(r'^cart/', include('satchless.cart.urls')),
        url(r'^checkout/', include('satchless.order.urls')),
        )

Run ``./manage.py syncdb`` to create the database tables.

Put initial settings for the product image files in ``settings.py``::

    SATCHLESS_IMAGE_SIZES = {
        'product-detail': {
            'size': (200, 150),
            'crop': False,
        }
    }

Shop, or just a product catalog?
................................

If you have enabled ``satchless.cart``, ``satchless.pricing`` or
``satchless.order`` app – which means you want to have anything more than just
a product catalog – you should also set the default currency the shop operates
in. ISO 3-letter codes are accepted, for example::

    SATCHLESS_DEFAULT_CURRENCY = 'EUR'

Also, base :ref:`pricing handler <pricing-overview>` should be configured, as
well as basic settings for :ref:`order handling <checkout-order>`::

    SATCHLESS_PRICING_HANDLERS = [
        'satchless.contrib.pricing.simpleqty.handler',
    ]
    SATCHLESS_ORDER_PARTITIONERS = [
        'satchless.contrib.order.partitioner.simple',
    ]
    SATCHLESS_DELIVERY_PROVIDERS = [
        'satchless.contrib.delivery.simplepost.provider',
    ]

Running
-------

Connect the application with your web server, or just run the development
server by typing ``./manage.py runserver``. Remeber not to use the development
server on production site!

For great success!

.. _`great documentation`: http://docs.djangoproject.com/en/1.2/intro/tutorial01/#creating-a-project
