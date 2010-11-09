.. _cart-wishlist:

==================
Wishlist as a cart
==================

Let's create a wishlist for our shop. A wishlist contains items similar to
these that go to the cart, and for that reason we're going to reuse the code
which handles the standard cart.

First of all, create a new app by ``django-admin.py startapp wishlist`` or
just make the files manually::

    wishlist/
        __init__.py
        forms.py
        listeners.py

The form
--------

We will reuse the standard ``AddToCart`` form, but hide the quantity input
field and ensure that every item goes to the wishlist with quantity set to 1.
Let's write our ``forms.py`` then::

    from django import forms
    from django.utils.translation import ugettext as _
    from satchless.cart.forms import AddToCartForm

    class AddToWishlistForm(AddToCartForm):
        def __init__(self, *args, **kwargs):
            super(AddToWishlistForm, self).__init__(*args, **kwargs)
            self.fields['quantity'].widget = forms.HiddenInput()

        def save(self, cart):
            cart.add_quantity(self.get_variant(), 1)

.. _cart-wishlist-signal:

The signal
----------

Now we should connect a listener which will produce *add to wishlist* forms
for every product being viewed. It goes to ``listeners.py`` file::

    from satchless.product.signals import product_view
    from satchless.cart.listeners import AddToCartListener
    from . import forms

    wishlist_listener = AddToCartListener(
            'satchless_wishlist',
            addtocart_formclass=forms.AddToWishlistForm,
            form_attribute='wishlist_form')
    product_view.connect(wisthlist_listener)

This requires a little explanation:

    * The cart type used for wishlists will be named ``satchless_wishlist``.
    * We have attached our fresh form class as the component for creating *add
      to wishlist* forms for products.
    * In the product view template every product instance will have the form
      stored under ``wishlist_form`` attribute.

.. note::
   You may also generate the listener inline, but remember to use strong
   reference, as it goes out of scope immediately. That means using
   ``weak=False`` parameter::

        product_view.connect(
            AddToCartListener(
                'satchless_wishlist',
                addtocart_formclass=forms.AddToWishlistForm,
                form_attribute='wishlist_form'),
            weak=False)

Finally, you should connect the listener when the application is being loaded,
by writing ``__init__.py`` file::

    import listeners

The template
------------

To show the form, we will override product template. The following snippet
shows what you could add to the standard template used in Satchless::

    {% if product.wishlist_form %}
    <form method="post" action="">
        {% csrf_token %}
        {{ product.wishlist_form.as_p }}
        <button type="submit">{% trans "Add to wishlist" %}</button>
    </form>
    {% endif %}

This template fragment checks for ``wishlist_form`` attribute in the product
instance (remember how we named it while :ref:`defining the signal listener
<cart-wishlist-signal>` above ?) and displays it if present.

.. note::
   To read more about how to override the standard templates without
   modifying original ones, have a look at `Django documentation on loading
   templates`_.

.. _`Django documentation on loading templates`: http://docs.djangoproject.com/en/1.2/ref/templates/api/#loading-templates

The workaround
--------------

Unfortunately, there is `a serious deficiency in Django`_ which requires us
to add a workaround in the main ``urls.py`` file::

    url(r'^cart/view/(?P<typ>satchless_cart|satchless_wishlist)/$',
        'satchless.cart.views.cart', name='satchless-cart-view'),

You should place it **before** the line which imports ``satchless.cart.urls``,
that looks like this::

    url(r'^cart/', include('satchless.cart.urls')),

It's also good to match the prefix and hide original cart view under the
workaround URL.

.. _`a serious deficiency in Django`: http://code.djangoproject.com/ticket/13154

Further customization
---------------------

When you have completed the tasks above, a nice *add to wishlist* form should
appear beside your products. You may also create a new template for the
wishlist, in order - for example - to hide the quantity field.

The cart view allows you to make separate templates for each cart type used in
the shop. It uses the following order of template lookup:

    * first, it looks for custom template, prefixed by the cart type, e.g.
      ``satchless/cart/satchless_wishlist/view.html``
    * if not present, the default template is being used:
      ``satchless/cart/view.html``
