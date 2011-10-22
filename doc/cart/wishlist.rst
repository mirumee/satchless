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
        app.py
        forms.py
        listeners.py

The app
-------

Let's start by creating a custom ``CartApp`` and giving it a new namespace and
a custom cart type. Do so in the ``app.py`` file::

    class WishlistApp(app.CartApp):
        app_name = 'wishlist'
        namespace = 'wishlist'
        cart_type = 'wishlist'

    wishlist_app = WishlistApp()

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

        def save(self):
            self.cart.add_quantity(self.get_variant(), 1)

.. _cart-wishlist-signal:

The signal
----------

Now we should create a handler which will produce *add to wishlist* forms
for every product being viewed. It uses the same class as the standard cart
does, and we will put it onto the top of our application module, that is
``__init__.py`` file::

    from satchless.cart.handler import AddToCartHandler
    from . import forms

    add_to_wishlist_handler = AddToCartHandler('wishlist',
                                               details_view='wishlist:details',
                                               addtocart_formclass=forms.AddToWishlistForm,
                                               form_attribute='wishlist_form')

This requires a little explanation:

    * The cart type used for wishlists will be named ``satchless_wishlist``.
    * We have attached our fresh form class as the component for creating *add
      to wishlist* forms for products.
    * In the product view template every product instance will have the form
      stored under ``wishlist_form`` attribute.

Finally, you should add the handler to the queue. Assuming that the standard cart
handler is already present, the corresponding setting would look like this::

    SATCHLESS_PRODUCT_VIEW_HANDLERS = [
        'satchless.cart.add_to_cart_handler',
        'wishlist.add_to_wishlist_handler',
    ]

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

The urls
--------

What remains to be done is placing our new application in the main ``urls.py``
file::

    url(r'^wishlist/$',include(wishlist_app.urls)),

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
