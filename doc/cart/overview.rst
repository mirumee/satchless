.. _cart-overview:

===============
Satchless carts
===============

Carts are containers which help customers with grouping items they are
interested in. The default behavior in majority of the shops is to have one
shopping cart per customer, and Satchless provides out-of-the-box method to
enable it.

However, you may allow multiple carts per customer to allow them managing more
sophisticated shopping.  Cart may also serve as wishlist, *save for later* list
or any other temporary storage.

Cart items consist of two values: :ref:`Variant <product-overview>` and
*quantity*.

Each cart is also described by a type. The default shopping cart
type is named ``satchless_cart``.

.. note::
   The field containing cart's type is called ``typ`` not to conflict with
   Python internal name of ``type``.

.. note::
   Unless Django project accepts `ticket #13154`_ the cart type will appear
   in URLs. For that reason, it's recommended to use type names which are
   URL-friendly.

.. _`ticket #13154`: http://code.djangoproject.com/ticket/13154

Carts can be owned by registered users or anonymous. The latter ones are
usually being used by customers who have not authorized themselves yet.

.. _cart-add-to-cart:

How to enable basic cart?
-------------------------

First of all, you should add the ``satchless.cart`` application to Django's
``INSTALLED_APPS`` list and run the ``syncdb`` command.

Second, add the following lines to ``settings.py``:

::

    SATCHLESS_PRODUCT_VIEW_HANDLERS = [
        'satchless.cart.add_to_cart_handler',
    ]

Now the cart is enabled. If you wish to know the topic better or use other cart
types, continue reading.

Adding to cart
--------------

Adding to cart mechanism uses a handler queue. The aim is to keep
``satchless.product`` and ``satchless.cart`` separated (i.e. keep only one-way
dependency). For that reason, the product view doesn't know anything about the
cart, wishlists etc. You have to process the data in handlers and display it in
the template layer.

When a product is about to be viewed, the ``SATCHLESS_PRODUCT_VIEW_HANDLERS``
queue is being run through. Each handler receives a list of product or variant
instances which have been selected to be displayed to the user. Each handler
may alter these instances or modify template context. The results are passed to
the next handler in the queue. A handler may also return a ``HttpResponse``
instance, which will be immediately passed to the user, stopping execution of
the handlers queue.

Behavior of the standard handler
................................

The standard handler (``satchless.cart.add_to_cart_handler``) finds the variant
selection form for every product or variant received. Then this form is merged
with another one, containing quantity and cart type, and together they build
a complete *add to cart* form.

Then, the resulting form is added to each product or variant instance, under
the ``cart_form`` attribute.

.. note::
    The attribute name and also the cart type can be easily changed. The
    standard handler uses ``satchless.cart.handler.AddToCartHandler`` which
    you may instatinate into a parametrized handler serving needs of your
    custom cart(s).

Depending on the request type, there are two actions possible:

    * If the request carries POST data - which usually happens after user has
      clicked *add to cart* button - the *add to cart* forms are being
      validated against it. The resulting variants are being put it into the
      cart and ``HttpResponse`` instance (with redirect to the cart page)
      is passed back.

    * If there is no POST data and the product is just being shown, or the
      validation of *add to cart* form has failed, the listener adds form to
      every product/variant instance received.

If no ``HttpResponse`` has broken execution of the queue, the standard template
is being rendered. By default it checks for cart forms and displays them if
present. By overriding the template, it's possible to display other forms too.

.. note::
   For more details, refer to the source code:

    * ``satchless/cart/handler.py``
    * ``satchless/product/views.py``
    * and ``satchless/product/templates/satchless/product/view.html``

