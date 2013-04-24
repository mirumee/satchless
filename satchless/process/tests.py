from unittest import TestCase

from . import ProcessManager, Step, InvalidData


class AddSwallows(Step):

    def __init__(self, data):
        self.data = data

    def __str__(self):
        return 'swallows-needed'

    def validate(self):
        if self.data.swallows < 2:
            raise InvalidData('Not enough swallows')


class AddCoconuts(Step):

    def __init__(self, data):
        self.data = data

    def __str__(self):
        return 'coconuts-needed'

    def validate(self):
        if self.data.coconuts < 1:
            raise InvalidData('Need a coconut')


class CoconutDelivery(ProcessManager):

    def __init__(self):
        self.swallows = 0
        self.coconuts = 0

    def __iter__(self):
        yield AddSwallows(self)
        yield AddCoconuts(self)


class ProcessManagerTest(TestCase):

    def test_iter(self):
        'ProcessManager.__iter__() returns the steps'
        process = CoconutDelivery()
        steps = map(str, list(process))
        self.assertEqual(steps, ['swallows-needed', 'coconuts-needed'])

    def test_get_next_step(self):
        'ProcessManager.get_next_step() returns the first step with invalid data'
        process = CoconutDelivery()
        process.coconuts = 1
        self.assertEqual(str(process.get_next_step()), 'swallows-needed')
        process.swallows = 2
        self.assertEqual(process.get_next_step(), None)
        process.coconuts = 0
        self.assertEqual(str(process.get_next_step()), 'coconuts-needed')

    def test_is_complete(self):
        'ProcessManager.is_complete() returns true if all steps are satisfied'
        process = CoconutDelivery()
        self.assertFalse(process.is_complete())
        process.coconuts = 1
        process.swallows = 2
        self.assertTrue(process.is_complete())

    def test_item_access(self):
        'You can index a ProcessManager using step names'
        process = CoconutDelivery()
        self.assertTrue(isinstance(process['coconuts-needed'], AddCoconuts))

        def invalid():
            return process['spam-needed']

        self.assertRaises(KeyError, invalid)

    def test_errors(self):
        'ProcessManager.get_errors() returns a dict of all invalid steps'
        process = CoconutDelivery()
        process.swallows = 2
        errors = process.get_errors()
        self.assertFalse('swallows-needed' in errors)
        self.assertTrue('coconuts-needed' in errors)
