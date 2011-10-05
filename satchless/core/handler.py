from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module


class QueueHandler(object):
    element_class = object
    require_unique_id = False

    def __init__(self, *elements, **kwargs):
        self.elements = elements
        if not kwargs.pop('lazy', False):
            self._build_queue()
        super(QueueHandler, self).__init__(**kwargs)

    def _build_queue(self):
        if not hasattr(self, '_queue'):
            queue = []
            registered_ids = set()
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
                    raise ImproperlyConfigured(u'%r in %s is not a proper subclass '
                                               u'of %s' %
                                               (item, self,
                                                self.element_class.__name__))
                unique_id = None
                if self.require_unique_id:
                    if not item.unique_id:
                        raise ImproperlyConfigured(u'%r in %s does not have a unique '
                                                   u'ID.' % (item, self))
                    if item.unique_id in registered_ids:
                        previous = dict(queue).get(item.unique_id)
                        raise ImproperlyConfigured(u'%r in %s provides an ID of %s that '
                                                   u'was already claimed by %r. Did you '
                                                   u'include the same object twice?' %
                                                   (item, self, item.unique_id,
                                                    previous))
                    registered_ids.add(item.unique_id)
                    unique_id = item.unique_id
                queue.append((unique_id, item))
            self._queue = queue
        return self._queue
    queue = property(_build_queue)
