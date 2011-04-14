.. _contrib-tax-flatgroups:

===============
Flat tax groups
===============

The ``satchless.contrib.tax.flatgroups`` allows defining flat tax rates for
groups of products. This would handle many popular taxing scenarios, including
VAT rates in EU.

There is also a possiblity to define a default group. Every product, which does
not belong to any other group, will be qualified as a member of the default one.

Installation
============

In this example we assume that you already use :ref:`simpleqty pricing module
<contrib-pricing-simpleqty>`. You may use any other pricing handler, the only
requirement is that we receive prices from element earlier in the
:ref:`pricing handler <pricing-overview>` chain. The ``flatgroups`` module
needs a value to operate on, it is not capable of fetching prices from database
or other storage.

Add the application to the ``INSTALLED_APPS`` list and the built-in provider
to the ``SATCHLESS_PRICING_HANDLERS`` chain::

    INSTALLED_APPS = (
        ...
        'satchless.pricing',
        'satchless.contrib.pricing.simpleqty',
        'satchless.contrib.tax.flatgroups',
    )

    SATCHLESS_PRICING_HANDLERS = [
        'satchless.contrib.pricing.simpleqty.handler',
        'satchless.contrib.tax.flatgroups.handler',
    ]

Usage
=====

In the admin form you will have to create tax groups. The group marked as
*default* will automatically include all the products that don't belong
to any other group.

There can be only one default group. If you mark one, the previous default
group loses it's status.
