.. _index:

=======================
Satchless: less is mo'
=======================

A shop for perfectionists with deadlines and coding standards.


Overview
========

Satchless is a high-level framework that provides building blocks for an online
store. In contrast to many other e-commerce solutions Satchless only delivers
the necessery bricks, not an out-of-the-box shop. By putting all the parts
together you can easily tailor the solution to meet your exact requirements
with no pain and no ugly workarounds.

It's based on `Django`_ web application framework and written in `Python`_ 
language. The aim of this project is to make each module independent and
extensible. Using Satchless you will be able to quickly build:

    * An online shop with:
        * shippable products
        * downloadable products
        * with both of them or any other product type you may imagine
        * discounts, wishlists and other popular features
        * custom checkout process
    * A cart which can be easily integrateed with many popular payment gateways
    * A catalog of products
    * A catalog with wishlists

.. _`Django`: http://djangoproject.org/
.. _`Python`: http://python.org/

The project is hosted on `GitHub`_, and the source code is available, as well as
an extensive test suite and some example applications.

.. _`GitHub`: http://github.com/mirumee/satchless

**Warning:** Satchless will shortly enter the beta stage of development and
it's currently perfectly possible to build a shop on top of it. However, you
should be prepared for some—sometimes also backward-incompatible—changes to
the code.


Main concepts
=============

Satchless is not a turn-key solution for online shops and is not meant to be
one. It should be considered to be a set of advanced, loosely coupled bricks
which can be turned into a working shop by a *programmer*.


The App
-------

The main idea behind the *Apps* is to provide an easy and flexible way of
extending Satchless. In short an *App* is a group of views sharing the same
logical and functional domain. The views are provided as methods of the *App*
object. You can treat the *App* itself as the context in which all of its views
execute. It means that apart from keeping the views logic, *App* is also
encapsulating the configuration (like model classes used by views, forms or
handlers).

Summarizing:

    * *App* is a group of views sharing same logical and functional domain
    * *App* is a context of view execution
    * *App* encapsulates the configuration ie. model classes used by views,
      forms, handlers etc.
    * In particular to the above *App* takes care of the URLs and the their
      namespace
    * *Apps* can be aware of other apps and use them instead of duplicating all
      the configuration (ie. an Order app uses the Cart app that in turn uses
      the Product app)

Satchless comes with a number of most important *Apps*. You can use them
out-of-the-box and/or easily extend or customise their behavior according to
your requirements:

    * **Product app** 
      :ref:`Details` |
      :ref:`Customisation example`
    * **Category app**
      :ref:`Details` |
      :ref:`Customisation example`
    * **Cart app**
      :ref:`Details` |
      :ref:`Customisation example`
    * **Order app**
      :ref:`Details` |
      :ref:`Customisation example`
    * **Checkout app** (abstract)
      :ref:`Details` |
      :ref:`Customisation example`


Deferred keys
-------------

Unfortunately, Django does not provide a pluggable way to say “here we want to
refer to an external model, unfortunately we don't know *which model* yet”.

There are possible workarounds like declaring a foreign key using the
`"module.Model"` syntax but we want Satchless to be a library. Thus we will
never tell you that you absolutely have to call your product model “Eels” and
keep it in a module named “hovercraft” lest everything falls apart.

Our solution is to introduce a pseudo-field type named `DeferredField`. It comes
in various flavors like `DeferredForeignKey` and `DeferredManyToManyField` and
provides an insertion point for a future relation. The relation itself can be
created by calling `satchless.utils.models.construct()`:

.. code-block:: python

    from django.db import models
    from satchless.utils.models import construct, DeferredForeignKey

    class AbstractTag(models.Model):

        parent = DeferredForeignKey('parent_model', related_name='tags')

        class Meta:
            abstract = True


    # Later on


    class MyModel(models.Model):

        title = models.CharField(max_length=100)


    class MyTag(construct(AbstractTag, parent_model=MyModel)):

        pass

Due to how Django works the implementation involves a touch of witchery so
should you absolutely hate it, you can still reconstruct the field as usual as
Django remains completely unaware of the deferred fields:

.. code-block:: python

    class MyTag(AbstractTag):

        parent = models.ForeignKey(MyModel, related_name='tags')


Magic Apps
----------

As much as we despise magic we also understand that it's important to provide
easy means to scaffold a working application. Satchless does not provide any
concrete models so getting started involved a fair share of work on your part.

To lower the barrier of entry we provide *MagicApps* that will take care of all
the model creation and let you get your feet wet without the risk of tripping.
*MagicApps* are flexible enough to allow you to override particular models while
having the rest of them constructed automatically. Please note however that we
do not encourage you to use *MagicApps* in a ready product as they are a hack
at best and subject to various limitations.

One important limitation you should be aware of is that *you can never have
more than one instance of the same MagicApp in the project*. This is because of
how Django register models and it's not something we plan to work around.


Domain driven models
--------------------

Main concepts behind Satchless models:

    * No *one-fits-all* approach
    * Single python class describes single class of products

If you already have some experience with other e-commerce platforms the above
statements might not sound and feel that natural at first glance
so let us draw some background behind them first. Most of the frameworks that we
came across in the past took quite the opposite direction.

Platforms like Satchmo, LFS or Oscar built their tightly coupled architectures
around a single Product model representing any of the products. Unfortunately,
even if this seems an obvious and handy choice it’s not likely to be the best
one in our opinion.

What we learnt is that the product’s model designed this way gets quickly
extremely inefficient and makes life harder in almost every aspect of further
development. It is especially true in case of custom, domain-driven e-commerce
solutions required to deal with millions of products and requests per day.


EAV vs Static classes
^^^^^^^^^^^^^^^^^^^^^

Let's talk about EAV approach first. It's evil.

When designing Product’s model around the “classic” concept you typically
use a single Product model, with a ProductClass and an Entity-Attribute-Value
approach to allow different kinds of products. Theoretically it allows to
create new kinds of products on the fly ie. via admin panel. Concern the
following issues introduced by this approach:

    * Despite creating new types of product through the admin, it’s very likely
      you will still want to provide product class-specific templates and
      logic like ie. variant forms.
    * The database structure for products gets complicated, which slows
      down even queries that might look (and should be) very simple
      at first glance. It might make data-intensive operations like
      import or migration tasks very time-consuming and complicated.
    * It's ugly. EAV sucks and we know it.

Basically, the main argument in favour of this approach is that it allows new
fields to be added quickly. But in practice it doesn't work out this way at all.

**In Satchless we use model inheritance and have different product classes
treated as real python classes instead.**

    * Static classes are good and everyone knows how to work with them.
    * One additional database table per product class, unless they need
      some new foreign key relationships.
    * Easier to do special logic on a per-class basis. Using the EAV
      approach, this will involve a whole new level of models, making the
      situation even worse.
    * Easier to work with data migration tasks.
    * No longer depend on fixtures to make the site work.
