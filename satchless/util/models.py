from collections import defaultdict
from django.db import models
from django.db.models.fields.related import SingleRelatedObjectDescriptor
from django.dispatch import receiver


class SubtypedManager(models.Manager):

    def find_subclasses(self, root):
        for a in dir(root):
            attr = getattr(root, a)
            if isinstance(attr, SingleRelatedObjectDescriptor):
                child = attr.related.model
                if (issubclass(child, root) and
                    child is not root):
                    yield a
                    for s in self.find_subclasses(child):
                        yield '%s__%s' % (a, s)

    # https://code.djangoproject.com/ticket/16572
    #def get_query_set(self):
    #    qs = super(SubtypedManager, self).get_query_set()
    #    subclasses = list(self.find_subclasses(self.model))
    #    if subclasses:
    #        return qs.select_related(*subclasses)
    #    return qs


class Subtyped(models.Model):

    subtype_attr = models.CharField(max_length=500, editable=False)
    __in_unicode = False

    objects = SubtypedManager()

    class Meta:
        abstract = True

    def __unicode__(self):
        # XXX: can we do it in more clean way?
        if self.__in_unicode:
            return unicode(super(Subtyped, self))
        subtype_instance = self.get_subtype_instance()
        if type(subtype_instance) is type(self):
            self.__in_unicode = True
            res = self.__unicode__()
            self.__in_unicode = False
            return res
        return subtype_instance.__unicode__()

    def get_subtype_instance(self):
        """
        Caches and returns the final subtype instance. If refresh is set,
        the instance is taken from database, no matter if cached copy
        exists.
        """
        subtype = self
        path = self.subtype_attr.split()
        whoami = self._meta.module_name
        remaining = path[path.index(whoami) + 1:]
        for r in remaining:
            subtype = getattr(subtype, r)
        return subtype

    def store_subtype(self, klass):
        if not self.id:
            path = [self]
            parents = self._meta.parents.keys()
            while parents:
                parent = parents[0]
                path.append(parent)
                parents = parent._meta.parents.keys()
            path = [p._meta.module_name for p in reversed(path)]
            self.subtype_attr = ' '.join(path)


@receiver(models.signals.pre_save)
def _store_content_type(sender, instance, **kwargs):
    if isinstance(instance, Subtyped):
        instance.store_subtype(instance)


class DeferredField(object):

    klass = models.Field

    def __init__(self, model_alias, **kwargs):
        self.model_alias = model_alias
        self.kwargs = kwargs

    def bind(self, model):
        return self.klass(model, **self.kwargs)


class DeferredForeignKey(DeferredField):

    klass = models.ForeignKey


class DeferredOneToOneField(DeferredField):

    klass = models.OneToOneField


class DeferredManyToManyField(DeferredField):

    klass = models.ManyToManyField


def __extract_deferred_fields(cls, current_class, results):
    for k, v in cls.__dict__.iteritems():
        if isinstance(v, DeferredField):
            # make sure it was not constructed earlier
            if isinstance(getattr(current_class, k), DeferredField):
                results[v.model_alias].append((k, v))
    for base in cls.__bases__:
        __extract_deferred_fields(base, current_class, results)


def construct(cls, **kwargs):
    needed_models = defaultdict(list)
    __extract_deferred_fields(cls, cls, needed_models)
    # construct correct fields for them
    new_fields = {}
    for model_alias, model in kwargs.iteritems():
        fields = needed_models.pop(model_alias, None)
        if not fields:
            raise TypeError('construct() got an unexpected keyword'
                            ' argument \'%s\'' % (model_alias, ))
        for field_name, field in fields:
            new_fields[field_name] = field.bind(model)
    # make sure no fields are missing
    if needed_models:
        raise TypeError('construct() did not get models for fields: %s' %
                        (', '.join(needed_models.keys()), ))

    # construct the Meta
    class Meta:
        abstract = True

    # create a list of attributes
    attrs = dict(new_fields, __module__=cls.__module__, Meta=Meta)
    key = tuple(new_fields.items())
    # try to cache results
    if not hasattr(cls, '_classcache'):
        cls._classcache = {}
    if not key in cls._classcache:
        clsname = '%s%x' % (cls.__name__, hash(key))
        clsname = clsname.replace('-', '_')
        cls._classcache[key] = type(clsname, (cls, ), attrs)
    return cls._classcache[key]
