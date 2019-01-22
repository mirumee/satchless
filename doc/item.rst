:mod:`satchless.item` --- abstract priceables
=============================================

.. module:: satchless.item

Available Types
---------------

All of the following types are abstract and meant to be subclassed to implement their missing methods.

.. note::

   Implementations provided by Satchless expect to work with money objects as implemented by the `prices <http://github.com/mirumee/prices>`_ library.

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

.. class:: ClassifyingPartitioner
   :noindex:

   A :class:`Partitioner` that automatically splits based on a classifying function.

.. class:: StockedItem
   :noindex:

   A stocked :class:`Item`. Introduces the concept of stock quantities.

.. class:: InsufficientStock
   :noindex:

   Exception class that is raised by :class:`StockedItem` when trying to exceed the stock quantity.


Available functions
-------------------

.. function:: partition(subject, keyfunc[, partition_class=ItemList])

   Returns a :class:`Partitioner` objects that splits `subject` based on the result of `keyfunc(item)`.


:class:`Item` Objects
---------------------

.. class:: Item

   An :class:`Item` instance represents a priceable item.

Instance methods:

.. method:: Item.get_price(**kwargs)

   Returns a :class:`prices.Money` or :class:`prices.TaxedMoney` object representing the price of the priceable.

   The default implementation passes all keyword arguments to :meth:`get_price_per_item`. Override to implement discounts and such.

For subclassing:

.. method:: Item.get_price_per_item(**kwargs)

   Returns a :class:`prices.Money` or :class:`prices.TaxedMoney` object representing the price for a single piece of the priceable.

   The default implementation will raise a :exc:`NotImplementedError` exception.

Example use::

   >>> import prices
   >>> from satchless.item import Item
   >>> class Coconut(Item):
   ...     def get_price_per_item(self): return prices.Money(10, currency='USD')
   ...
   >>> coconut = Coconut()
   >>> coconut.get_price()
   Money('10', currency='USD')


:class:`ItemRange` Objects
--------------------------

.. class:: ItemRange

   An :class:`ItemRange` instance represents a range of priceables.

Instance methods:

.. method:: ItemRange.__iter__()

   Returns an iterator yielding priceable objects that implement a ``get_price()`` method.

   The default implementation will raise a :exc:`NotImplementedError` exception.

.. method:: ItemRange.get_price_range(**kwargs)

   Returns a :class:`prices.MoneyRange` or :class:`prices.TaxedMoneyRange` object representing the price range of the priceables included in the range object. Keyword arguments are passed to :meth:`get_price_per_item`.

   Calling this method on an empty range will raise an :exc:`AttributeError` exception.

For subclassing:

.. method:: ItemRange.get_price_per_item(item, **kwargs)

   Return a :class:`prices.Money` or :class:`prices.TaxedMoney` object representing the price of a given item.

   The default implementation will pass all keyword arguments to ``item.get_price()``. Override to implement discounts or caching.

Example use::

   >>> import prices
   >>> from satchless.item import Item, ItemRange
   >>> class SpanishInquisition(Item):
   ...     def get_price_per_item(self): return prices.Money(50, currency='BTC')
   ...
   >>> class LaVache(Item):
   ...     def get_price_per_item(self): return prices.Money(15, currency='BTC')
   ...
   >>> class ThingsNobodyExpects(ItemRange):
   ...     def __iter__(self):
   ...         yield SpanishInquisition()
   ...         yield LaVache()
   ...
   >>> tne = ThingsNobodyExpects()
   >>> tne.get_price_range()
   MoneyRange(Money('15', currency='BTC'), Money('50', currency='BTC'))


:class:`ItemLine` Objects
-------------------------

.. _item-line-class:

.. class:: ItemLine

   An :class:`ItemLine` instance represents a certain quantity of a particular priceable.

Instance methods:

.. method:: ItemLine.get_total(**kwargs)

   Return a :class:`prices.Money` or :class:`prices.TaxedMoney` object representing the total price of the line. Keyword arguments are passed to both :meth:`get_quantity` and :meth:`get_price_per_item`.

For subclassing:

.. method:: ItemLine.get_quantity(**kwargs)

   Returns an :class:`int` or a :class:`decimal.Decimal` representing the quantity of the item.

   The default implementation will ignore all keyword arguments and always return ``1``.

.. method:: ItemLine.get_price_per_item(**kwargs)

   Returns a :class:`prices.Money` or :class:`prices.TaxedMoney` object representing the price of a single piece of the item.

   The default implementation will raise a :exc:`NotImplementedError` exception.

Example use::

   >>> import prices
   >>> from satchless.item import ItemLine
   >>> class Shrubberies(ItemLine):
   ...     def __init__(self, qty): self.qty = qty
   ...     def get_quantity(self): return self.qty
   ...     def get_price_per_item(self): return prices.Money(11, currency='GBP')
   ... 
   >>> shrubberies = Shrubberies(7)
   >>> shrubberies.get_total()
   Money('77', currency='GBP')


:class:`ItemSet` Objects
------------------------

.. _item-set-class:

.. class:: ItemSet

   An :class:`ItemSet` instance represents a set of :class:`ItemLine` or other :class:`ItemSet` objects that has a total price.

Instance methods:

.. method:: ItemSet.__iter__()

   Returns an iterator yielding objects that implement a ``get_total()`` method. Good candidates include instances of :class:`ItemLine` and :class:`ItemSet` itself.

   The default implementation will raise a :exc:`NotImplementedError` exception.

.. method:: ItemSet.get_total(**kwargs)

   Return a :class:`prices.Money` or :class:`prices.TaxedMoney` object representing the total price of the set. Keyword arguments are passed to :meth:`get_subtotal`.

   Calling this method on an empty set will raise an :exc:`AttributeError` exception.

For subclassing:

.. method:: ItemSet.get_subtotal(item, **kwargs)

   Returns a :class:`prices.Money` or :class:`prices.TaxedMoney` object representing the total price of ``item``.

   The default implementation will pass keyword arguments to ``item.get_total()``. Override to implement discounts or caching.

Example use::

   >>> import prices
   >>> from satchless.item import Item, ItemLine, ItemSet
   >>> class Product(Item):
   ...     def get_price_per_item(self): return prices.Money(10, currency='EUR')
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
   Money('50', currency='EUR')


:class:`Partitioner` Objects
----------------------------

.. class:: Partitioner(subject)

   A :class:`Partitioner` instance is an iterable view of the ``subject`` that partitions it for purposes such as split delivery.

Instance methods:

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
   [ItemList(['a', 'c', 'e']), ItemList(['b', 'd', 'f'])]

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
           if remaining:
               yield ItemList(remaining)


:class:`ClassifyingPartitioner` Objects
---------------------------------------

.. class:: ClassifyingPartitioner(subject)

   A :class:`Partitioner` subclass that splits the subject into groups based on the result of the classifying method.

Instance methods:

.. method:: ClassifyingPartitioner.classify(item)

   Returns a classification key that groups together items that are meant for the same group.

   The default implementation will raise a :exc:`NotImplementedError` exception.

Example use:

   >>> from satchless.item import ItemList, ClassifyingPartitioner
   >>> class ClassNameSplitter(ClassifyingPartitioner):
   ...     def classify(self, item):
   ...         return type(item).__name__
   ... 
   >>> splitter = ClassNameSplitter(['a', 'b', 1, ['one'], 2, ['two']])
   >>> list(splitter)
   [ItemList([1, 2]), ItemList([['one'], ['two']]), ItemList(['a', 'b'])]



:class:`StockedItem` Objects
----------------------------

.. class:: StockedItem

   A :class:`StockedItem` object is subclass of :class:`Item` that allows you to track stock quantities and guard against excess allocation.

Instance methods:

.. method:: ItemSet.get_stock()

   Returns the current stock quantity of the item.

   The default implementation will raise a :exc:`NotImplementedError` exception.

.. method:: StockedItem.check_quantity(quantity)

   Makes sure that at least `quantity` of the object are in stock by comparing the value with the result of `self.get_stock()`.
   If there is not enough, an :class:`InsufficientStock` exception will be raised.

Example use:

   >>> from satchless.item import InsufficientStock, StockedItem
   >>> class LimitedShrubbery(StockedItem):
   ...     def get_stock(self):
   ...         return 1
   ... 
   >>> shrubbery = LimitedShrubbery()
   >>> try:
   ...     shrubbery.check_quantity(2)
   ... except InsufficientStock as e:
   ...     print('only %d remaining!' % (e.item.get_stock(),))
   ... 
   only 1 remaining!


:class:`InsufficientStock` Exception
------------------------------------

.. class:: InsufficientStock(item)

   Informs you that a stock quantity check failed against `item`. Raised by :meth:`StockedItem.check_quantity`.
