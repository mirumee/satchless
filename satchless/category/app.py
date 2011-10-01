from django.conf.urls.defaults import patterns, url
from django.http import Http404
from django.http import HttpResponseNotFound

from ..product import app
from . import models

class CategorizedProductApp(app.ProductApp):
    app_name = 'satchless-category'
    category_model = models.Category
    category_details_templates = [
        'satchless/category/%(category_app)s/%(category_model)s/view.html',
        'satchless/category/%(category_app)s/view.html',
        'satchless/category/view.html',
    ]
    category_list_templates = [
        'satchless/category/%(category_app)s/%(category_model)s/list.html',
        'satchless/category/%(category_app)s/list.html',
        'satchless/category/list.html',
    ]
    allow_uncategorized_product_urls = False

    def path_from_slugs(self, slugs):
        """
        Returns list of Category instances matching given slug path.
        """
        if len(slugs) == 0:
            return []
        leaves = self.category_model.objects.filter(slug=slugs[-1])
        if not leaves:
            raise self.category_model.DoesNotExist, "slug='%s'" % slugs[-1]
        for leaf in leaves:
            path = leaf.get_ancestors()
            if len(path) + 1 != len(slugs):
                continue
            if [c.slug for c in path] != slugs[:-1]:
                continue
            return list(path) + [leaf]
        raise self.category_model.DoesNotExist

    def category_list(self, request):
        return self.respond(request, self.get_context_data(request))

    def category_details(self, request, parent_slugs, category_slug):
        slugs = filter(None, parent_slugs.split('/') + [category_slug])
        try:
            path = self.path_from_slugs(slugs)
        except self.category_model.DoesNotExist:
            return HttpResponseNotFound()
        category = path[-1]
        context = self.get_context_data(request, category=category, path=path)
        return self.respond(request, context, category=category)

    def get_template_names(self, product=None, category=None, **kwargs):
        if product:
            template_data = {
                'product_app': product._meta.module_name,
                'product_model': product._meta.object_name.lower(),
            }
            template_names = self.product_details_templates
        elif category:
            template_data = {
                'category_app': category._meta.module_name,
                'category_model': category._meta.object_name.lower(),
            }
            template_names = self.category_details_templates
        else:
            template_data = {
                'category_app': self.category_model._meta.module_name,
                'category_model': self.category_model._meta.object_name.lower(),
            }
            template_names = self.category_list_templates
        return [t % template_data for t in template_names]

    def get_context_data(self, request, product=None, **kwargs):
        categories = self.category_model.objects.filter(parent__isnull=True)
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
        products = self.product_model.objects.all()
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

    def get_urls(self, prefix=None):
        prefix = prefix or 'satchless-category'
        url_patterns = patterns('',
            # '+' predeces product slug to prevent conflicts with categories
            # paths
            url(r'^$', self.category_list,
                name='%s-list' % prefix),
            # this url simplifies url templatetag usage ({% url slug %} instead of {% url '' slug %})
            url(r'^(?P<category_slug>[a-z0-9_-]+)/$',
                self.category_details, name='%s-details' % prefix,
                kwargs={'parent_slugs': ''}),
            url(r'^(?P<parent_slugs>([a-z0-9_-]+/)*)(?P<category_slug>[a-z0-9_-]+)/$',
                self.category_details, name='%s-details' % prefix),
            url(r'^(?P<category_slugs>([a-z0-9_-]+/)+)\+(?P<product_slug>[a-z0-9_-]+)/$',
                self.product_details, name='%s-product-details' % prefix),
        )
        if self.allow_uncategorized_product_urls:
            url_patterns += super(CategorizedProductApp, self).get_urls()
        return url_patterns

product_app = CategorizedProductApp()
