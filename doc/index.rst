.. _index:

=======================
Satchless - less is mo'
=======================

A shop for perfectionists with deadlines and coding standards.

Overview
========

Satchless is a high level framework which provides parts to build an online
shop. It's based on `Django`_ web application framework and written in
`Python`_ language. The aim of this project is to make each module
independent and extensible. Using Satchless you will be able to build quickly:

    * A product catalog
    * A catalog with wishlists
    * An online shop with:
        * shippable products,
        * downloadable products
        * with both of them or any other product type you may imagine.

.. note::
   Satchless is not a turn-key solution for online shop and is not aimed to be.
   It should be considered as a set of advanced, loosely coupled bricks which
   would be turned into a working shop by a web developer.

.. _`Django`: http://djangoproject.org/
.. _`Python`: http://python.org/

First steps
===========

    * **Running Satchless:**
      :ref:`Requirements <intro-requirements>` |
      :ref:`Installation <intro-installation>`
    * **Out of the box:**
      :ref:`Creating a product catalog <intro-products>` |
      :ref:`Creating a simple shop <intro-simpleshop>`

Customizing your shop
=====================

    * **Products:**
      :ref:`Overview <product-overview>` |
      :ref:`Writing custom product models <product-custom_models>` |
      :ref:`Product sets <product-sets>`
    * **Customers:**
    * **Carts and lists:**
      :ref:`Carts overview <cart-overview>` |
      :ref:`Wishlist as a cart <cart-wishlist>`
    * **Prices and taxes:**
      :ref:`Pricing overview <pricing-overview>` |
      :ref:`Writing your own price or tax handler <pricing-handler>`
    * **Checkout:**
      :ref:`Orders <checkout-order>` |
      :ref:`Shipping, payment and routers <checkout-router>`
    * **Payments:**
