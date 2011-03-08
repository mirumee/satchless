# -*- coding:utf-8 -*-
import os
import re

PROJECT_ROOT = os.path.dirname( __file__ )

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'dev.db',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Warsaw'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en'
LANGUAGES = (
    ('en', u"English"),
)
PREFIX_DEFAULT_LOCALE = True

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/'
STATIC_URL = '/static/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = STATIC_URL + 'grappelli/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'm+q17zt_)tsu+-=9gi)4g%66rys*bn9rw5w*v$xxkh%dua*7_8'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'localeurl.middleware.LocaleURLMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'pagination.middleware.PaginationMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_ROOT, 'templates'),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
#    'grappelli.context_processors.admin_template_path',
    'mothertongue.context_processors.router',
)
STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, "static"),
)


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'localeurl',
    'mothertongue',
    'grappelli',
    'django.contrib.admin',
    'mptt',
    'countries',
    'satchless.product',
    'satchless.image',
    #'satchless.contrib.examples.dummy',
    #'satchless.contrib.examples.parrot',
    #'satchless.contrib.productset',
    #'satchless.contact',
    'satchless.cart',
    'satchless.pricing',
    'satchless.contrib.pricing.simpleqty',
    'satchless.contrib.tax.flatgroups',
    #'satchless.contrib.stock.singlestore',
    'satchless.order',
    #'satchless.contrib.delivery.simplepost',
    'products',
    'south',
    'pagination',
    'sale',
)

SATCHLESS_IMAGE_SIZES = {
    'admin': {
        'size': (100, 100),
        'crop': True,
    },
    'category': {
        'size': (230, 257),
        'crop': True,
    },
    'category-product': {
        'size': (230, 307),
        'crop': True,
    },
    'product-detail': {
        'size': (460, 900),
        'crop': False,
    },
    'product-thumb': {
        'size': (55, 74),
        'crop': True,
    },
    'product-cart': {
        'size': ('98', '135'),
        'crop': True,
    }
}

SATCHLESS_DEFAULT_CURRENCY = '£' #'GBP'

INTERNAL_IPS = ['127.0.0.1']

SATCHLESS_PRICING_HANDLERS = [
    'satchless.contrib.pricing.simpleqty.handler',
    'satchless.contrib.tax.flatgroups.handler',
    'sale.handler',
]
SATCHLESS_PRODUCT_VIEW_HANDLERS = [
    'core.handler.cart_handler',
]
#
#SATCHLESS_ORDER_PARTITIONERS = [
#    'satchless.contrib.order.partitioner.simple',
#]
#
#SATCHLESS_DELIVERY_PROVIDERS = [
#    'satchless.contrib.delivery.simplepost.providers.PostDeliveryProvider',
#]
#
#INTERNAL_IPS = ['127.0.0.1']
#
#try:
#    execfile(os.path.join(PROJECT_ROOT, 'local_settings.py'))
#except IOError:
#    pass

try:
    execfile(os.path.join(PROJECT_ROOT, 'local_settings.py'))
except IOError:
    pass
