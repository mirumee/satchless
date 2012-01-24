import satchless.util.tests

from categories.app import product_app
from .app import wishlist_app
import products.models


class ViewsTestCase(satchless.util.tests.ViewsTestCase):
    def setUp(self):
        self.category = product_app.Category.objects.create(name='posh',
                                                            slug='posh')
        self.product = products.models.Hat.objects.create(name='top hat',
                                                          slug='top-hat',
                                                          price=10)
        self.product.categories.add(self.category)

    def _get_or_create_cart_for_client(self, cart_app, client=None):
        client = client or self.client
        self._test_status(cart_app.reverse('details'),
                          client_instance=client)
        token = client.session[cart_app.cart_session_key]
        return cart_app.Cart.objects.get(token=token)

    def test_add_to_wishlist(self):
        wishlist = self._get_or_create_cart_for_client(wishlist_app,
                                                       client=self.client)
        # wishlist var indicates which handler should serve this request
        data = {
            'wishlist': 'wishlist',
        }
        self._test_POST_status(self.product.get_absolute_url(),
                               data=data, status_code=302,
                               client_instance=self.client)
        self.assertEqual([i.variant.get_subtype_instance().product for i in wishlist.get_all_items()],
                         [self.product])

    def test_add_to_cart_from_wishlist(self):
        wishlist = self._get_or_create_cart_for_client(wishlist_app)
        # add item to wishlist
        wishlist_item = wishlist.add_item(self.product.variants.get(), 1).cart_item
        # move item from wishlist into cart
        add_to_cart_url = wishlist_app.reverse('add-to-cart', args=(wishlist_item.pk,))
        self._test_POST_status(add_to_cart_url, status_code=302,
                               client_instance=self.client)

        # check cart content
        cart = self._get_or_create_cart_for_client(wishlist_app.cart_app)
        cart_items = cart.get_all_items()
        self.assertEqual(len(cart_items), 1)
        self.assertEqual(cart_items[0].variant.get_subtype_instance(),
                         wishlist_item.variant.get_subtype_instance())
