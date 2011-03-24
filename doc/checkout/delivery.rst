.. _checkout-delivery:

========
Delivery
========

Means of delivery are the main factor influencing the way in which orders are
processed. Satchless supports multiple delivery types per order and puts all
the order items into *delivery groups* (even if there is only one delivery
method, the entire content of order is put into a single group).

The process of processing delivery information during checkout is, roughly,
following:

    * group items into delivery groups,
    * for each group check available delivery types,
    * ask customer to select the delivery method for each of the groups,
    * if needed, ask about details for the methods chosen.

.. _checkout-delivery-partitioners:

Partitioners: Grouping order items
----------------------------------

The code responsible for distributing items among delivery groups is called
*partitioner*. It is usually a custom code designed for specific shop instance.
Satchless comes with one default partitoner,
``satchless.contrib.order.partitioner.simple``, which puts all the items into
a single group.

.. note::
   A bookstore, for example, may use a custom partitioner which puts dead-tree
   books into one group for post shipping and ebooks into another group for
   immediate download.

You may use a single partitioner which is aware of all the products available
in the shop, but you may, as well, have a collection of less advanced
partitioners that only know how to deal with a specific subset of the products.
The partitioners are chained together in a queue defined by
``SATCHLESS_ORDER_PARTITIONERS`` setting.

Each member of the queue is given a list of remaining (ungrouped) items. It
returns a list of groups it decided to create, and a list of remaining items
which is passed to the next partitioner. The only requirement is to have all
the order items grouped after the queue has been finished.

.. _checkout-delivery-providers:

Providers: Querying for delivery types
--------------------------------------

After the items have been grouped, it's time to ask for available delivery
methods for each of the groups. Another queue,
``SATCHLESS_DELIVERY_PROVIDERS``, does that. Each delivery group is passed
through this queue and each provider may add a list of delivery types
available for this group.

.. note::
   In a bookstore mentioned above, this is a moment to assign download method
   to the group containing ebooks and post/messenger/pickup to the others.

Delivery details
----------------

After the delivery types have been chosen, every provider involved is asked for
an optional details form. Usually, we ask there for the shipping address. If no
provider returned a form, we skip to the payment step.

This is a good place to do your customization. Satchless comes with an
:ref:`address book <contacts>` and it would be a good idea to copy customer's
default shipping address into forms here.

