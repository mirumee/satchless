from django.conf import settings
from django.utils.importlib import import_module
from django.http import HttpResponse

_handlers_queue = None

def product_view(instances, request):
    context = {}
    for handler in _handlers_queue:
        context = handler(instances, request=request, extra_context=context)
        if isinstance(context, HttpResponse):
            return context
    return context

def init_queue():
    global _handlers_queue
    _handlers_queue = []
    for handler in getattr(settings, 'SATCHLESS_PRODUCT_VIEW_HANDLERS', []):
        if isinstance(handler, str):
            mod_name, han_name = handler.rsplit('.', 1)
            module = import_module(mod_name)
            handler = getattr(module, han_name)
        _handlers_queue.append(handler)

init_queue()
