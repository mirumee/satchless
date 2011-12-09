#!/usr/bin/env python
import os

from django.core.management import call_command

os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'

if __name__ == "__main__":
    call_command('test')