.. _contrib-pricing-simpleqty:

======================================
Simple pricing with quantity discounts
======================================

The ``satchless.contrib.pricing.simpleqty`` application provides a simple
pricing module which would satisfy needs of most online stores. It does
support quantity-based discounts and handles only one currency.

This module does not handle any taxing. For that, see :ref:`flatgroups
<contrib-tax-flatgroups>` application.

Installation
============

Add the application to the ``INSTALLED_APPS`` list and the built-in provider
to the ``SATCHLESS_PRICING_HANDLERS`` chain::

    INSTALLED_APPS = (
        ...
        'satchless.pricing',
        'satchless.contrib.pricing.simpleqty',
    )

    SATCHLESS_PRICING_HANDLERS = [
        'satchless.contrib.pricing.simpleqty.handler',
    ]

Usage
=====

*Simpleqty* should appear in the admin index. There you may add a price
entry for each product. The options are:

    * **Quantity pricing mode:** How the discounts are being made – depending
      on product or variant quantity. See below for explanation.
    * **Base price:** The entry price before any discounts or variant-related
      changes are applied.
    * **Price qty overrides:** How the quantity overrides the base price. When
      customer orders at least *minimal quantity* of the item, the unit price
      changes to *unit price* specified here. Always the rule with biggest
      applicable *minimal quantity* is used.
    * **Variant price offsets:** How the price changes for each variant. This
      is an absolute value in the shop currency. It can be positive or negative.
      For example, with a base price of 8€ for a t-shirt and -2€ ofset for the
      green variant, the unit price of a green t-shirt results in 6€.

Per-product and per-variant discounts
-------------------------------------

This setting determines whether the quantity of a single variant or of all
the variants of the product whould be considered when calculating a discount.

For example, you are going to sell **T-shirt** with a base price of **$10**.
You have also defined:
    * *Quantity override*: **$8** for minimal quantity of **10 items**,
    * *Variant offset*: **+$2** for **red t-shirt**.

The cart contains:
    * 6 green t-shirts
    * 10 blue t-shirts
    * 8 red t-shirts

With **per-product** pricing all the items qualify for discount because there
are more than 10 t-shirts:

============= === ========== =========
Item          Qty Unit price     Price
============= === ========== =========
green t-shirt   6          8        48
blue t-shirt   10          8        80
red t-shirt     8         10        80
**TOTAL**                      **208**
============= === ========== =========

But with **per-variant** pricing, only the blue ones qualify. The result
would be:

============= === ========== =========
Item          Qty Unit price     Price
============= === ========== =========
green t-shirt   6         10        60
blue t-shirt   10          8        80
red t-shirt     8         12        96
**TOTAL**                      **236**
============= === ========== =========
