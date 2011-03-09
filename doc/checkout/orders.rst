.. _checkout-order:

=====
Order
=====

Order is a snapshot of a cart with all customer, delivery and billing data
added. It does not change after it has been processed, no matter what changes
have been made to the products, prices or other data involved in the creation
of the order.

Therefore, ``Order`` and ``OrderItem`` objects hold a copy of the cart from
the time of pressing the *checkout* button.

Delivery groups and partitioners
--------------------------------

An order can be divided into several *delivery groups*. For example, if you
sell ebooks on numismatics, antique coins and refrigerators to keep them, you
may wish to enable download of the ebook immediately after the order has been
paid, send coins by messenger on the next day and ask wholesaler to send
refrigerator to the customer's address as soon as it arrives from the factory
(and hope the coins would survive until then ;)

The piece of code resposible for partitioning an order into delivery groups is,
surprisingly, called a *partitioner*. To read more, see the
:ref:`delivery section <checkout-delivery>`.

================
Checkout process
================

The default checkout process consists of 3 to 5 internal steps:

    * **Step 1**: The order is partitioned into delivery groups and customer
      is asked to choose a delivery method for each of them.
    * **Step 1½**: If a delivery method requires any additional data (the
      address, for example), the customer is asked for it.
    * **Step 2**: The customer is being asked for the payment method.
    * **Step 2½**: If the payment method requires any additional data, the
      customer is asked for it.
    * **Step 3**: Confirmation. The complete order data is being presented
      and the customer is being asked for confirmation. This screen will
      usually redirect the customer to the appropriate payment gateway.
