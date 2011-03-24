.. _index:

=======================
Satchless - less is mo'
=======================

A shop for perfectionists with deadlines and coding standards.

Overview
========

Satchless is a high level framework that provides building blocks for an online
shop. It's based on `Django`_ web application framework and written in
`Python`_ language. The aim of this project is to make each module
independent and extensible. Using Satchless you will be able to quickly build:

    * A product catalog
    * A catalog with wishlists
    * An online shop with:
        * shippable products,
        * downloadable products
        * with both of them or any other product type you may imagine.

.. _`Django`: http://djangoproject.org/
.. _`Python`: http://python.org/

.. note::
   Satchless is not a turn-key solution for online shops and is not meant to be
   one. It should be considered as a set of advanced, loosely coupled bricks
   which can be turned into a working shop by a web developer.

**Warning:** Currently Satchless is in an early stage of development. It is
already possible to build a shop on top of it, but still you should be prepared
for radical and backward-incompatible changes to the code.

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
      :ref:`Contacts <contacts>`
    * **Carts and lists:**
      :ref:`Carts overview <cart-overview>` |
      :ref:`Wishlist as a cart <cart-wishlist>`
    * **Prices and taxes:**
      :ref:`Pricing overview <pricing-overview>` |
      :ref:`Writing your own price or tax handler <pricing-handler>`
    * **Checkout:**
      :ref:`Introduction to orders <checkout-order>` |
      :ref:`Delivery: partitioners and providers <checkout-delivery>` |
      :ref:`Payment <checkout-payment>`

Reference
=========

     * :ref:`Settings <reference-settings>` – complete list of configuration
       parameters read from the ``settings`` module.
