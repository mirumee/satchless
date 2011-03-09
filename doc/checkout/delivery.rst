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

Grouping order items
--------------------

The code responsible for distributing items among delivery groups is called
*partitioner*. It is usually a custom code designed for specific shop instance.
Satchless comes with one default partitoner,
``satchless.contrib.order.partitioner.simple``, which puts all the items into
a single group.

.. note::
   A bookstore, for example, may use simple partitioner which puts dead-tree
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
