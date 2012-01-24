import satchless.cart.handler

from . import forms

class AddToCartHandler(satchless.cart.handler.AddToCartHandler):
    def __init__(self, **kwargs):
        kwargs['addtocart_formclass'] = kwargs.get('addtocart_formclass',
                                                   forms.AddToCartForm)
        super(AddToCartHandler, self).__init__(**kwargs)

    def __call__(self, instances=None, request=None, extra_context=None, **kwargs):
        if request and (request.method == 'GET' or (request.method == 'POST' and
                                                    self.cart_app.app_name in request.POST)):
            return super(AddToCartHandler, self).__call__(instances=instances, request=request,
                                                          extra_context=extra_context, **kwargs)
        return extra_context


class AddToWishlistHandler(AddToCartHandler):
    def __init__(self, **kwargs):
        kwargs['addtocart_formclass'] = kwargs.get('addtocart_formclass',
                                                   forms.AddToWishlistForm)
        kwargs['form_attribute'] = kwargs.get('form_attribute',
                                              'wishlist_form')
        super(AddToWishlistHandler, self).__init__(**kwargs)

