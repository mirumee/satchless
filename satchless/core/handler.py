from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module


class QueueHandler(object):
    element_class = object
    require_unique_id = False

    def __init__(self, *elements):
        self.queue = self.build_queue(elements)

    def build_queue(self, elements):
        queue = []
        registered_ids = set()
        for item in elements:
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
        return queue
