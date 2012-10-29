import satchless.util.tests

from categories.app import product_app
from .app import wishlist_app, cart_app
import products.models


class ViewsTestCase(satchless.util.tests.ViewsTestCase):
    def setUp(self):
        self.category = product_app.Category.objects.create(name='posh',
                                                            slug='posh')
        self.hat = products.models.Hat.objects.create(name='top hat',
                                                      slug='top-hat',
                                                      price=10)
        self.hat.categories.add(self.category)
        self.variant = self.hat.variants.create(sku='sku', stock_level=10)

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
        self._test_POST_status(self.hat.get_absolute_url(),
                               data=data, status_code=302,
                               client_instance=self.client)
        self.assertEqual([i.variant.get_subtype_instance().product for i in wishlist.get_all_items()],
                         [self.hat])

    def test_add_to_cart(self):
        cart = self._get_or_create_cart_for_client(cart_app,
                                                       client=self.client)
        # cart var indicates which handler should serve this request
        data = {
            'cart': 'cart',
            'quantity': 1,
        }
        self._test_POST_status(self.hat.get_absolute_url(),
                               data=data, status_code=302,
                               client_instance=self.client)
        self.assertEqual([i.variant.get_subtype_instance().product for i in cart.get_all_items()],
                         [self.hat])

    def test_add_to_cart_fails_when_variant_is_out_of_stock(self):
        cart = self._get_or_create_cart_for_client(cart_app,
                                                       client=self.client)
        # cart var indicates which handler should serve this request
        data = {
            'cart': 'cart',
            'quantity': 1,
        }
        variant = self.hat.variants.get()
        variant.stock_level = 0
        variant.save()
        response = self._test_POST_status(self.hat.get_absolute_url(),
                                          data=data, status_code=200,
                                          client_instance=self.client)
        self.assertEqual(len(cart.get_all_items()), 0)
        cart_form = response.context['product'].cart_form
        self.assertTrue('__all__' in cart_form.errors)

    def test_add_to_cart_from_wishlist(self):
        wishlist = self._get_or_create_cart_for_client(wishlist_app)
        # add item to wishlist
        wishlist_item = wishlist.add_item(self.hat.variants.get(), 1).cart_item
        # move item from wishlist into cart
        response = self._test_GET_status(wishlist_app.reverse('details'),
                                         client_instance=self.client)
        form = response.context['cart_item_forms'][0]
        data = {
            form.add_prefix('request_marker'): '',
        }
        self._test_POST_status(
            wishlist_app.reverse('details'), status_code=302,
            client_instance=self.client,
            data=data,
        )

        # check cart content
        cart = self._get_or_create_cart_for_client(wishlist_app.cart_app)
        cart_items = cart.get_all_items()
        self.assertEqual(len(cart_items), 1)
        self.assertEqual(cart_items[0].variant.get_subtype_instance(),
                         wishlist_item.variant.get_subtype_instance())
        self.assertEqual(cart_items[0].quantity, 1)

    def test_add_to_cart_from_wishlist_fails_when_variant_is_out_of_stock(self):
        self.variant.stock_level = 0
        self.variant.save()
        wishlist = self._get_or_create_cart_for_client(wishlist_app)
        # add item to wishlist
        wishlist.add_item(self.variant, 1)
        # add item to wishlist
        wishlist_url = wishlist_app.reverse('details')
        # move item from wishlist into cart
        response = self._test_GET_status(wishlist_url,
                                         client_instance=self.client)
        form = response.context['cart_item_forms'][0]
        self._test_POST_status(
            wishlist_url, status_code=200,
            client_instance=self.client,
            data={form.add_prefix('request_marker'): ''}
        )

        # check cart content
        cart = self._get_or_create_cart_for_client(wishlist_app.cart_app)
        cart_items = cart.get_all_items()
        self.assertEqual(len(cart_items), 0)
