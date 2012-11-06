from django.http import Http404
from django.http import HttpResponseNotFound
from django.template.response import TemplateResponse

from ..core.app import view
from ..product import app
from ..product import models as product_models
from ..util.models import construct
from . import models


class CategorizedProductApp(app.ProductApp):

    app_name = 'category'
    Category = None
    category_details_templates = [
        'satchless/category/%(category_model)s/view.html',
        'satchless/category/view.html',
    ]
    category_list_templates = [
        'satchless/category/%(category_model)s/list.html',
        'satchless/category/list.html',
    ]

    def __init__(self, *args, **kwargs):
        super(CategorizedProductApp, self).__init__(*args, **kwargs)
        assert self.Category, ('You need to subclass CategorizedProductApp and'
                               ' provide Category')

    def path_from_slugs(self, slugs):
        """
        Returns list of Category instances matching given slug path.
        """
        if len(slugs) == 0:
            return []
        leaves = self.Category.objects.filter(slug=slugs[-1])
        if not leaves:
            raise self.Category.DoesNotExist, "slug='%s'" % slugs[-1]
        for leaf in leaves:
            path = leaf.get_ancestors()
            if len(path) + 1 != len(slugs):
                continue
            if [c.slug for c in path] != slugs[:-1]:
                continue
            return list(path) + [leaf]
        raise self.Category.DoesNotExist

    @view(r'^$', name='category-index')
    def category_list(self, request):
        context = self.get_context_data(request)
        format_data = {
            'category_model': self.Category._meta.module_name,
        }
        templates = [p % format_data for p in self.category_list_templates]
        return TemplateResponse(request, templates, context)

    @view(r'^(?P<category_slug>[a-z0-9_-]+)/$', name='category-details',
          kwargs={'parent_slugs': ''})
    @view(r'^(?P<parent_slugs>([a-z0-9_-]+/)*)(?P<category_slug>[a-z0-9_-]+)/$',
          name='category-details')
    def category_details(self, request, parent_slugs, category_slug):
        slugs = filter(None, parent_slugs.split('/') + [category_slug])
        try:
            path = self.path_from_slugs(slugs)
        except self.Category.DoesNotExist:
            return HttpResponseNotFound()
        category = path[-1]
        context = self.get_context_data(request, category=category, path=path)
        format_data = {
            'category_model': category._meta.module_name,
        }
        templates = [p % format_data for p in self.category_details_templates]
        return TemplateResponse(request, templates, context)

    @view(r'^(?P<category_slugs>([a-z0-9_-]+/)+)\+(?P<product_pk>[0-9]+)-(?P<product_slug>[a-z0-9_-]+)/$',
          name='details')
    def product_details(self, request, **kwargs):
        return super(CategorizedProductApp, self).product_details(request,
                                                                  **kwargs)

    def get_context_data(self, request, product=None, **kwargs):
        categories = self.Category.objects.filter(parent__isnull=True)
        context = dict(kwargs, categories=categories)
        if product:
            context.update({
                'path': product.category_path,
                'product': product,
            })
        return context

    def get_product(self, request, category_slugs='', product_slug=None,
                    product_pk=None):
        slugs = category_slugs.split('/')
        path = self.path_from_slugs(filter(None, slugs))
        products = self.Product.objects.all()
        if product_slug:
            products = products.filter(slug=product_slug)
        if product_pk:
            products = products.filter(pk=product_pk)
        if len(path):
            products = products.filter(categories=path[-1])
        elif not request.user.is_staff:
            products = products.filter(categories__isnull=False)
        if not products.exists():
            raise Http404()
        product = products[0].get_subtype_instance()
        product.category_path = path
        return product


class MagicCategorizedProductApp(CategorizedProductApp, app.MagicProductApp):

    def __init__(self, **kwargs):
        self.Category = (self.Category or
                         self.construct_category_class())
        self.Product = (self.Product or
                        self.construct_product_class(self.Category))
        super(MagicCategorizedProductApp, self).__init__(**kwargs)

    def construct_product_class(self, category_class):
        class Product(construct(models.CategorizedProductMixin,
                                category=category_class),
                      product_models.Product):
            pass

        return Product

    def construct_category_class(self):
        class Category(models.Category):
            pass
        return Category
