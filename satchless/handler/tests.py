from unittest import TestCase

from . import Handler, filter_handlers


class IntegerHandler(Handler):

    def __init__(self, subject):
        self.subject = subject

    def __eq__(self, other):
        if not isinstance(other, IntegerHandler):
            return NotImplemented
        return self.subject == other.subject

    @classmethod
    def can_handle(cls, subject):
        return isinstance(subject, int)


class StringHandler(Handler):

    def __init__(self, subject):
        self.subject = subject

    def __eq__(self, other):
        if not isinstance(other, StringHandler):
            return NotImplemented
        return self.subject == other.subject

    @classmethod
    def can_handle(cls, subject):
        return isinstance(subject, str)


class HandlerTest(TestCase):

    def test_handlers_for(self):
        int_handlers = filter_handlers([IntegerHandler, StringHandler], 42)
        self.assertEqual(list(int_handlers), [IntegerHandler(42)])
        str_handlers = filter_handlers([IntegerHandler, StringHandler], 'ni!')
        self.assertEqual(list(str_handlers), [StringHandler('ni!')])
