from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module


class QueueHandler(object):
    element_class = object

    def __init__(self, *elements, **kwargs):
        self.elements = elements
        if not kwargs.pop('lazy', False):
            self._build_queue()
        super(QueueHandler, self).__init__(**kwargs)

    @property
    def queue(self):
        return self._build_queue()

    def _build_queue(self):
        if not hasattr(self, '_queue'):
            queue = []
            for item in self.elements:
                if isinstance(item, str):
                    mod_name, attr_name = item.rsplit('.', 1)
                    module = import_module(mod_name)
                    if not hasattr(module, attr_name):
                        raise ImproperlyConfigured(
                            u'%s in %s does not exist.' % (item, self))
                    item = getattr(module, attr_name)
                if isinstance(item, type):
                    item = item()
                if not isinstance(item, self.element_class):
                    raise ImproperlyConfigured(u'%r in %s is not a proper'
                                               u' subclass of %s.' %
                                               (item, self,
                                                self.element_class.__name__))
                queue.append(item)
            self._queue = queue
        return self._queue