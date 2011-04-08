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

Satchless applications
----------------------

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
        )

Run ``./manage.py syncdb`` to create the database tables.

Put initial settings for the product image files in ``settings.py``::

    SATCHLESS_IMAGE_SIZES = {
        'product-detail': {
            'size': (200, 150),
            'crop': False,
        }
    }

The last thing you need to do is set the default currency for your store. To do so, add SATCHLESS_DEFAULT_CURRENCY to your settings.py, setting its value to a three-letter ISO code::

    SATCHLESS_DEFAULT_CURRENCY = 'USD'

Running
-------

Connect the application with your web server, or just run the development
server by typing ``./manage.py runserver``. Remeber not to use the development
server on production site!

For great success!

.. _`great documentation`: http://docs.djangoproject.com/en/1.2/intro/tutorial01/#creating-a-project
