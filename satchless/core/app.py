# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url
from django.core.urlresolvers import reverse
from django.shortcuts import redirect


class SatchlessApp(object):

    app_name = None
    namespace = None

    def __init__(self, name=None):
        self.app_name = name or self.app_name

    def get_context_data(self, request, **kwargs):
        context = {
            'current_app': self.app_name,
        }
        context.update(kwargs)
        return context

    def redirect(self, to, *args, **kwargs):
        uri = self.reverse(to, args=args, kwargs=kwargs)
        return redirect(uri)

    def reverse(self, to, args=None, kwargs=None):
        to = '%s:%s' % (self.namespace, to)
        return reverse(to, args=args, kwargs=kwargs, current_app=self.app_name)

    def get_urls(self):
        urls = []
        klass = type(self)
        # walk the class as walking the instance evaluates descriptors which is
        # a Really Bad Idea™
        for item in dir(klass):
            obj = getattr(klass, item)
            # look for methods
            if hasattr(obj, 'im_func'):
                method = getattr(self, item)
                for regex, params in getattr(obj, '_routes', []):
                    urls.append(url(regex=regex, view=method, **params))
        return patterns('', *urls)

    @property
    def urls(self):
        return self.get_urls(), self.app_name, self.namespace


def view(regex, **kwargs):
    def view(func):
        if not hasattr(func, '_routes'):
            func._routes = []
        func._routes.append((regex, kwargs))
        return func
    return view
