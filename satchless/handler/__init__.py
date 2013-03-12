class Handler(object):
    """
    An action carrier
    """
    @classmethod
    def can_handle(cls, *args, **kwargs):
        raise NotImplementedError()  # pragma: no cover


def filter_handlers(handler_candidates, *args, **kwargs):
    for handler_class in handler_candidates:
        if handler_class.can_handle(*args, **kwargs):
            yield handler_class(*args, **kwargs)
