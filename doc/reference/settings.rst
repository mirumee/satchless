.. _reference-settings:

==================
Satchless settings
==================

The following list describes all the settings Satchless is able to recognize.
All of them go to the ``settings.py`` file. To learn about the settings in
general, refer to `Django settings`_ doc.

.. _`Django settings`: http://docs.djangoproject.com/en/1.3/topics/settings/

SATCHLESS_COUNTRY_CHOICES
-------------------------

A list of countries your business cares about. If not set, Satchless will
default to a list of all known countries. Valid values are:

* an iterable of 2-letter country ISO codes with optional separators expressed
  as ``None``::

      SATCHLESS_COUNTRY_CHOICES = ('GB', 'US', None, 'CZ', 'PL')

* an iterable of choices, using valid 2-letter country ISO codes as values::

      SATCHLESS_COUNTRY_CHOICES = (
          ('CZ', 'The guys who make beer'),
          ('PL', 'The guys who drink it'),
      )

* a callable returning any of the above::

      SATCHLESS_COUNTRY_CHOICES = lambda: ['BE', 'DE', 'FR']

* a Python path to any of the above::

      SATCHLESS_COUNTRY_CHOICES = 'my_store.stuff.country_list'

SATCHLESS_DEFAULT_CURRENCY
--------------------------

The default currency Satchless operates in. It should be set in a form of ISO
3-letter code. Examples: ``EUR``, ``USD``, ``PLN``.

SATCHLESS_DELIVERY_PROVIDERS
----------------------------

A list of :ref:`Delivery Providers <checkout-delivery-providers>`. Python paths
should be used for clarity, but direct use of providers' instances is also
accepted.  Example::

    import myapp

    SATCHLESS_DELIVERY_PROVIDERS = [
        'satchless.contrib.delivery.pocztapolska.provider',
        'myshipping.messenger_delivery_provider',
        myapp.delivery_provider
    ]

SATCHLESS_DJANGO_PAYMENT_TYPES
------------------------------

Used by ``satchless.contrib.payment.django_payments_provider``. Should be a
sequence of ``django_payments`` backends allowed to be used within Satchless
shop. Example::

    SATCHLESS_DJANGO_PAYMENT_TYPES = ('dummy', 'dotpay')

SATCHLESS_IMAGE_SIZES
---------------------

A dictionary of allowed image sizes. The ``at_size`` template tag from
``satchless.image`` application accepts one of it's keys as an argument.
Example::

    SATCHLESS_IMAGE_SIZES = {
        'admin': {
            'size': (100, 100),
            'crop': True,
        },
        'product-detail': {
            'size': (460, 900),
            'crop': False,
        },
        'product-thumb': {
            'size': (55, 74),
            'crop': True,
        }
    }

SATCHLESS_ORDER_PARTITIONERS
----------------------------

A list of :ref:`Order Partitioners <checkout-delivery-partitioners>`. Python
paths and instances are accepted. The syntax is the same as for
``SATCHLESS_DELIVERY_PROVIDERS``.

SATCHLESS_PAYMENT_PROVIDERS
---------------------------

A list of :ref:`Payment Providers <checkout-payment>`. Python paths and
instances are accepted. The syntax is the same as for
``SATCHLESS_DELIVERY_PROVIDERS``.

SATCHLESS_PRODUCT_VIEW_HANDLERS
-------------------------------

A list of product view handlers. :ref:`Adding to cart <cart-add-to-cart>` and
:ref:`adding to wishlist <cart-wishlist>` are fine examples of use. Python
paths and instances are accepted. The syntax is the same as for
``SATCHLESS_DELIVERY_PROVIDERS``.

SATCHLESS_PRICING_HANDLERS
--------------------------

A list of pricing handlers. :ref:`Simple pricing with quantity discounts
<contrib-pricing-simpleqty>` and caching handlers
(satchless.contrib.pricing.cache.CacheFactory) are good examples of use.
Python paths and instances are accepted. The syntax is the same as for 
``SATCHLESS_DELIVERY_PROVIDERS``.

Note that at the moment settings.py by default provides caching handlers so
any change in product's price requires cache entry to expire in order to see the
new price being applied online (by default Django keeps cache in memory so it
will be dropped with server restart).
