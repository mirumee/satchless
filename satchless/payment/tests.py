"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

import datetime
from django import forms
from django.test import TestCase

from . import fields
from . import models
from . import PaymentProvider

class TestPaymentVariant(models.PaymentVariant):
    pass


class TestPaymentProvider(PaymentProvider):
    unique_id = 'test'

    def enum_types(self, order=None, customer=None):
        return (('gold', 'gold'),)

    def get_configuration_form(self, order, typ, data):
        return None

    def create_variant(self, order, typ, form):
        payment_variant = TestPaymentVariant.objects.create(order=order,
                                                            price=0,
                                                            name='test')
        return payment_variant

    def confirm(self, order):
        pass

class CreditCardNumberFieldTest(TestCase):
    def setUp(self):
        self.field = fields.CreditCardNumberField()

    def test_valid_number(self):
        TEST_NUMBERS = [
            # VISA
            '4111 1111 1111 1111',
            # MasterCard
            '5500 0000 0000 0004',
            '5424 0000 0000 0015',
            # American Express
            '3782 8224 6310 005',
            '3400 0000 0000 009',
            '3700 0000 0000 002',
            # Discover
            '6011 1111 1111 1117',
            '6011 0000 0000 0004',
            '6011 0000 0000 0012',
            # Diner's Club
            '3000 0000 0000 04',
            '2014 0000 0000 009',
            # JCB
            '3088 0000 0000 0009',
        ]
        for number in TEST_NUMBERS:
            self.assertTrue(self.field.clean(number))

    def test_invalid_number(self):
        INVALID_NUMBERS = [
            '9999 9999 9999 9999',
            'abc',
            '--',
        ]
        for number in INVALID_NUMBERS:
            self.assertRaises(forms.ValidationError, self.field.clean,
                              number)


class CreditCardExpirationFieldTest(TestCase):
    def setUp(self):
        self.field = fields.CreditCardExpirationField()

    def test_valid_date(self):
        expires = datetime.date.today() + datetime.timedelta(days=30)
        self.assertTrue(self.field.clean(expires))

    def test_past_date(self):
        expires = datetime.date.today() + datetime.timedelta(days=-60)
        self.assertRaises(forms.ValidationError, self.field.clean,
                          expires)
