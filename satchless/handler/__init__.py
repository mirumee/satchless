class Handler(object):
    """
    An action carrier
    """
    def __new__(cls, subject):
        if not cls.can_handle(subject):
            raise ValueError("%r does know how to handle %r" % (cls, subject))
        return object.__new__(cls, subject)

    def __init__(self, subject):
        self.subject = subject

    @classmethod
    def can_handle(cls, subject):
        raise NotImplementedError()  # pragma: no cover


def handlers_for(subject, handler_candidates):
    for handler_class in handler_candidates:
        try:
            yield handler_class(subject)
        except ValueError:
            pass
