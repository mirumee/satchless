.. _pricing-overview:

===========================
Pricing and taxing overview
===========================

Satchles comes with support for pluggable price handlers. A handler can do
anything with a price before it's shown to customer or put into an order,
for example:

    * extract the price from database (or any other data source),
    * calculate discounts for multiple-item purchase,
    * add tax,
    * calculate special discounts: temporary sales, promotions, discounts
      for regular customers, etc.

Handlers can be chained together, to process the prices in defined order.
The setting ``SATCHLESS_PRICING_HANDLERS`` is a list of modules or other
objects which extract or modify the price.

Each of the handlers accepts price(s) from the previous one and returns
same set of data to be processed in the next step. Of course, you should
configure it wisely and ensure that first handler does not require input
data, but fetches it from database or any storage of your preference.

Standard handlers in satchless
------------------------------

Here's an example of standard configuration, using modules provided by
satchless::

    SATCHLESS_PRICING_HANDLERS = [
        'satchless.contrib.pricing.simpleqty.handler',
        'satchless.contrib.tax.flatgroups.handler',
    ]

The first step is ``satchless.contrib.pricing.simpleqty`` module, responsible
for storing and retrieving prices for products and variants. It has limited
set of basic features:

    * Each product can have a base price.
    * Each variant can have a price modifier (called *offset*) to the base
      product price.
    * Each product can have special prices for larger quantities. They can
      work in two modes: *per variant* when the minimal quantity of single
      variant is present in the cart, or *per product* when the quantity
      of all product's variants in the cart reaches the limit.

The second step is taxing module in ``satchless.contrib.tax.flatgroups``
defines groups of products with different tax rates. It can also have a
default "catch-all" group. The price given by former handler is being
processed here and used on the shop pages.

Price objects
-------------

Satchless uses special ``satchless.pricing.Price`` objects internally. Each
of them represents a double price set: ``net`` and ``gross``. In a shop where
taxing is not being handled, usually they contain the same value.

These objects can handle a limited set of operations. For example, you may
add two ``Price`` objects together, but multiplication may use a single-number
object as the second argument (e.g. ``int``, ``Decimal`` and also ``float``
which is not recommended due to limited precision, unacceptable in monetary
operations).

The ``Price`` object may carry additional data, like *tax name* which holds
a short description of the tax rate applied. In most cases, you have to take
care of this data being transferred to new ``Price`` objects you create.
