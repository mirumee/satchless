:mod:`satchless.cart` --- shopping carts
========================================

.. module:: satchless.cart

Available Types
---------------

All of the following types are abstract and meant to be subclassed to implement their missing methods.

.. note::

   Implementations provided by Satchless expect to work with price objects as implemented by the `prices <http://github.com/mirumee/prices>`_ library.

.. class:: CartLine
   :noindex:

   A single line in a shopping cart. Describes a product, its quantity and (optinal) data. Attributes: :attr:`product`, :attr:`quantity`, :attr:`data`.

   Suitable for pickling.

.. class:: Cart
   :noindex:

   A shopping cart. Contains a number of :class:`CartLine` objects.

   Suitable for pickling.


:class:`CartLine` Objects
-------------------------

.. class:: CartLine(product, quantity, data=None)

   A :class:`CartLine` object represents a single line in a shopping cart. It subclasses the :ref:`ItemLine <item-line-class>`.

   You should not have to create instances of this class manually. Use the :meth:`Cart.add` method and let it construct lines as needed instead.

Instance methods:

.. method:: CartLine.get_total(**kwargs)

   See :ref:`ItemLine <item-line-class>`.

For subclassing:

.. method:: CartLine.get_price_per_item(**kwargs)

   See :ref:`ItemLine <item-line-class>`.

   The default implementation passes all keyword arguments to ``self.product.get_price()``. Override to implement discounts or caching.


:class:`Cart` Objects
---------------------

.. class:: Cart(items=None)

   A :class:`Cart` object represents a shopping cart. It subclasses the :ref:`ItemSet <item-set-class>`.

Instance attributes:

.. attribute:: modified

   ``True`` if the object was modified since it was created/deserialized. ``False`` otherwise.

   Useful if you need to persist the cart.

Instance methods:

.. method:: Cart.__iter__()

   Returns an iterator that yields :class:`CartLine` objects contained in the cart.

   See :ref:`ItemSet <item-set-class>`.

.. method:: Cart.add(product, quantity=1, data=None, replace=False)

   If ``replace`` is ``False``, increases quantity of the given product by ``quantity``. If given product is not in the cart yet, a new line is created.

   If ``replace`` is ``True``, quantity of the given product is set to ``quantity``. If given product is not in the cart yet, a new line is created.

   If the resulting quantity of a product is zero, its line is removed from the cart.

   Products are considered identical if both ``product`` and ``data`` are equal. This allows you to customize two copies of the same product (eg. choose different toppings) and track their quantities independently.

.. method:: Cart.get_total(**kwargs)

   Return a :class:`prices.Price` object representing the total price of the cart.

   See :ref:`ItemSet <item-set-class>`.

For subclassing:

.. method:: Cart.check_quantity(product, quantity, data)

   Checks if given quantity is valid for the product and its data.

   Default implementation does nothing. Override and raise a meaningful exception if given quantity is invalid.

.. method:: Cart.create_line(product, quantity, data)

   Creates a :class:`CartLine` given a product, its quantity and data. Override to use a custom line class.

Example use::

   >>> import prices
   >>> from satchless.item import Item
   >>> from satchless.cart import Cart
   >>> class Taco(Item):
   ...     def __repr__(self): return 'Taco()'
   ...     def get_price_per_item(self): return prices.Price(5, currency='CHF')
   ... 
   >>> cart = Cart()
   >>> veggie_taco = Taco()
   >>> cart.add(veggie_taco, quantity=3, data=['extra cheese'])
   >>> cart.add(veggie_taco, data=['very small rocks'])
   >>> cart.add(veggie_taco, data=['very small rocks'])
   >>> list(cart)
   [CartLine(product=Taco(), quantity=3, data=['extra cheese']),
    CartLine(product=Taco(), quantity=2, data=['very small rocks'])]
   >>> cart.get_total()
   Price('25', currency='CHF')
