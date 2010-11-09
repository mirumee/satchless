.. _cart-overview:

===============
Satchless carts
===============

Carts are containers which help customers with grouping items they are
interested in. The default behavior is to have one shopping cart per
customer, but you may allow multiple carts per customer to allow them
managing more sophisticated shopping. Cart may also serve as wishlist,
*save for later* list or any other temporary storage.

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

Adding to cart
--------------

Adding to cart mechanism uses signals quite extensively. The aim is to keep
``satchless.product`` and ``satchless.cart`` separated (i.e. keep only one-way
dependency).

When a product is being viewed, the ``satchless.product.signals.product_view``
is sent. The cart application listens to it and gets variant selection form for
every product or variant passed with the signal. Another signal,
``satchless.product.signals.variant_formclass_for_product`` is used to do that.
The form is merged together with another one containing quantity and cart type,
and together they form complete *add to cart* form.

Depending on the request type, there are two actions possible:

    * If the request carries POST data, the *add to cart* forms are being
      validated against it. The resulting variants are being put it into the
      cart and response object (with redirect to the cart page) is passed back.

    * If there is no POST data or validation has failed, the listener adds
      form to every product/variant instance received.

After the signal has been handled, the product view looks for any response
objects returned by listener(s). If there is a response, it's being served.

Otherwise, the standard template is being rendered. By default it checks for
cart forms and displays them if present. By overriding the template, it's
possible to display other forms too.

.. note::
   For more details, refer to the source code:

    * ``satchless/cart/listeners.py``
    * ``satchless/product/views.py``
    * and ``satchless/product/templates/satchless/product/product.html``

