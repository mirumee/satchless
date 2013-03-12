from unittest import TestCase

from . import Handler, handlers_for


class IntegerHandler(Handler):

    def __eq__(self, other):
        if not isinstance(other, IntegerHandler):
            return NotImplemented
        return self.subject == other.subject

    @classmethod
    def can_handle(cls, subject):
        return isinstance(subject, int)


class StringHandler(Handler):

    def __eq__(self, other):
        if not isinstance(other, StringHandler):
            return NotImplemented
        return self.subject == other.subject

    @classmethod
    def can_handle(cls, subject):
        return isinstance(subject, str)


class HandlerTest(TestCase):

    def test_can_handle(self):
        int_handler = IntegerHandler(42)
        self.assertTrue(isinstance(int_handler, IntegerHandler))

        def pass_str():
            return IntegerHandler('what is your favourite colour?')

        self.assertRaises(ValueError, pass_str)

    def test_handlers_for(self):
        int_handlers = handlers_for(42, [IntegerHandler, StringHandler])
        self.assertEqual(list(int_handlers), [IntegerHandler(42)])
        str_handlers = handlers_for('ni!', [IntegerHandler, StringHandler])
        self.assertEqual(list(str_handlers), [StringHandler('ni!')])
