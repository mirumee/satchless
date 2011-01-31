from django.contrib.contenttypes.models import ContentType
from django.db import models

class Subtyped(models.Model):
    content_type = models.ForeignKey(ContentType, editable=False)
    _subtype_instance = None
    __in_unicode = False

    def get_subtype_instance(self, refresh=False):
        """
        Caches and returns the final subtype instance. If refresh is set,
        the instance is taken from database, no matter if cached copy
        exists.
        """
        if not self._subtype_instance or refresh:
            self._subtype_instance = self.content_type.get_object_for_this_type(pk=self.pk)
        return self._subtype_instance

    def store_content_type(self, klass):
        self.content_type = ContentType.objects.get_for_model(klass)

    def __unicode__(self):
        # XXX: can we do it in more clean way?
        if self.__in_unicode:
            return super(Subtyped, self).__unicode__()
        elif type(self.get_subtype_instance()) == type(self):
            self.__in_unicode = True
            res = self.__unicode__()
            self.__in_unicode = False
            return res
        else:
            return self.get_subtype_instance().__unicode__()

    class Meta:
        abstract = True

def _store_content_type(sender, instance, **kwargs):
    if isinstance(instance, Subtyped):
        instance.store_content_type(sender)
models.signals.pre_save.connect(_store_content_type)
