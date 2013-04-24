:mod:`satchless.item` --- abstract priceables
=============================================

.. module:: satchless.item

Available Types
---------------

All of the following types are abstract and meant to be subclassed to implement their missing methods.

.. note::

   Implementations provided by Satchless expect to work with price objects as implemented by the `prices <http://github.com/mirumee/prices>`_ library.

.. class:: Item
   :noindex:

   A priceable item. Usually a single product or a single product variant.

.. class:: ItemRange
   :noindex:

   A range of priceables that vary in price. An example is a product with multiple variants.

.. class:: ItemLine
   :noindex:

   A certain amount of an :class:`Item`. Contains a priceable and its quantity. An example is a cart line.

.. class:: ItemSet
   :noindex:

   A collection of :class:`ItemLine` objects that have a total price. Examples include a bundle, an order or a shopping cart.

.. class:: ItemList
   :noindex:

   An :class:`ItemSet` that subclasses the Python :class:`list`.

.. class:: Partitioner
   :noindex:

   An object capable of partitioning an :class:`ItemSet` into multiple sets for purposes such as split delivery.


:class:`Item` Objects
---------------------

.. class:: Item

   An :class:`Item` instance represents a priceable item.

   Use the :meth:`get_price` method to retrieve the price of a priceable instance.

For subclassing:

.. method:: Item.get_price_per_item(**kwargs)

   Returns a :class:`prices.Price` object representing the price for a single piece of the priceable.

   The default implementation will raise a :exc:`NotImplementedError` exception.

Public methods:

.. method:: Item.get_price(**kwargs)

   Returns a :class:`prices.Price` object representing the price of the priceable.

   The default implementation passes all keyword arguments to :meth:`get_price_per_item`. Override to implement discounts and such.

Example use::

   >>> import prices
   >>> from satchless.item import Item
   >>> class Coconut(Item):
   ...     def get_price_per_item(self): return prices.Price(10, currency='USD')
   ...
   >>> coconut = Coconut()
   >>> coconut.get_price()
   Price('10', currency='USD')


:class:`ItemRange` Objects
--------------------------

.. class:: ItemRange

   An :class:`ItemRange` instance represents a range of priceables.

   Use the :meth:`get_price_range` method to retrieve the price range of the range instance.

For subclassing:

.. method:: ItemRange.__iter__()

   Returns an iterator yielding priceable objects that implement a ``get_price()`` method.

   The default implementation will raise a :exc:`NotImplementedError` exception.

.. method:: ItemRange.get_price_per_item(item, **kwargs)

   Return a :class:`prices.Price` object representing the price of a given item.

   The default implementation will pass all keyword arguments to ``item.get_price()``. Override to implement discounts or caching.

Public methods:

.. method:: ItemRange.get_price_range(**kwargs)

   Returns a :class:`prices.PriceRange` object representing the price range of the priceables included in the range object. Keyword arguments are passed to :meth:`get_price_per_item`.

   Calling this method on an empty range will raise an :exc:`AttributeError` exception.

Example use::

   >>> import prices
   >>> from satchless.item import Item, ItemRange
   >>> class SpanishInquisition(Item):
   ...     def get_price_per_item(self): return prices.Price(50, currency='BTC')
   ...
   >>> class LaVache(Item):
   ...     def get_price_per_item(self): return prices.Price(15, currency='BTC')
   ...
   >>> class ThingsNobodyExpects(ItemRange):
   ...     def __iter__(self):
   ...         yield SpanishInquisition()
   ...         yield LaVache()
   ...
   >>> tne = ThingsNobodyExpects()
   >>> tne.get_price_range()
   PriceRange(Price('15', currency='BTC'), Price('50', currency='BTC'))


:class:`ItemLine` Objects
-------------------------

.. class:: ItemLine

   An :class:`ItemLine` instance represents a certain quantity of a particular priceable.

   Use the :meth:`get_total` method to retrieve the total price.

For subclassing:

.. method:: ItemLine.get_quantity(**kwargs)

   Returns an :class:`int` or a :class:`decimal.Decimal` representing the quantity of the item.

   The default implementation will ignore all keyword arguments and always return ``1``.

.. method:: ItemLine.get_price_per_item(**kwargs)

   Returns a :class:`prices.Price` object representing the price of a single piece of the item.

   The default implementation will raise a :exc:`NotImplementedError` exception.

Public methods:

.. method:: ItemLine.get_total(**kwargs)

   Return a :class:`prices.Price` object representing the total price of the line. Keyword arguments are passed to both :meth:`get_quantity` and :meth:`get_price_per_item`.

Example use::

   >>> import prices
   >>> from satchless.item import ItemLine
   >>> class Shrubberies(ItemLine):
   ...     def __init__(self, qty): self.qty = qty
   ...     def get_quantity(self): return self.qty
   ...     def get_price_per_item(self): return prices.Price(11, currency='GBP')
   ... 
   >>> shrubberies = Shrubberies(7)
   >>> shrubberies.get_total()
   Price('77', currency='GBP')


:class:`ItemSet` Objects
------------------------

.. class:: ItemSet

   An :class:`ItemSet` instance represents a set of :class:`ItemLine` or other :class:`ItemSet` objects that has a total price.

   Use the :meth:`get_total` method to retrieve the total price.

For subclassing:

.. method:: ItemSet.__iter__()

   Returns an iterator yielding objects that implement a ``get_total()`` method. Good candidates include instances of :class:`ItemLine` and :class:`ItemSet` itself.

   The default implementation will raise a :exc:`NotImplementedError` exception.

.. method:: ItemSet.get_subtotal(item, **kwargs)

   Returns a :class:`prices.Price` object representing the total price of ``item``.

   The default implementation will pass keyword arguments to ``item.get_total()``. Override to implement discounts or caching.

Public methods:

.. method:: ItemSet.get_total(**kwargs)

   Return a :class:`prices.Price` object representing the total price of the set. Keyword arguments are passed to :meth:`get_subtotal`.

   Calling this method on an empty set will raise an :exc:`AttributeError` exception.

Example use::

   >>> import prices
   >>> from satchless.item import Item, ItemLine, ItemSet
   >>> class Product(Item):
   ...     def get_price_per_item(self): return prices.Price(10, currency='EUR')
   ... 
   >>> class CartLine(ItemLine):
   ...     def __init__(self, product, qty): self.product, self.qty = product, qty
   ...     def get_price_per_item(self): return self.product.get_price()
   ...     def get_quantity(self): return self.qty
   ... 
   >>> class Cart(ItemSet):
   ...     def __iter__(self):
   ...         yield CartLine(Product(), 5)
   ... 
   >>> cart = Cart()
   >>> cart.get_total()
   Price('50', currency='EUR')


:class:`Partitioner` Objects
----------------------------

.. class:: Partitioner(subject)

   A :class:`Partitioner` instance is an iterable view of the ``subject`` that partitions it for purposes such as split delivery.

For subclassing:

.. method:: Partitioner.__iter__()

   Returns an iterator that yields :class:`ItemSet` objects representing partitions of ``self.subject``.

   The default implementation will yield a single :class:`ItemList` containing all the elements of ``self.subject``. Override to implement your partitioning scheme.

Example use:

   >>> from satchless.item import ItemList, Partitioner
   >>> class EvenOddSplitter(Partitioner):
   ...     def __iter__(self):
   ...         yield ItemList(it for n, it in enumerate(self.subject) if not n % 2)
   ...         yield ItemList(it for n, it in enumerate(self.subject) if n % 2) 
   ... 
   >>> splitter = EvenOddSplitter(['a', 'b', 'c', 'd', 'e', 'f'])
   >>> list(splitter)
   [['a', 'c', 'e'], ['b', 'd', 'f']]

A more advanced example could split an imaginary cart object into groups of objects that can be delivered together::

   from satchless.item import ItemList, Partitioner

   class DeliveryPartitioner(Partitioner):

       def __iter__(self):
           """
           Yield single-product groups for products that need to be shipped
           separately. Yield a separate group for digital products if present.
           Everything else can be shipped together.
           """
           digital = []
           remaining = []
           for it in self.subject:
               if it.ship_separately:
                   yield ItemList([it])
               elif it.is_digital:
                   digital.append(it)
               else:
                   remaining.append(it)
           if digital:
               yield ItemList(digital)
           if the_rest:
               yield ItemList(remaining)
