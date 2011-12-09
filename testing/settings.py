import os

AUTHNET_LOGIN_ID = ''
AUTHNET_TRANSACTION_KEY = ''

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3'
    },
}

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',

    'django_nose',
    'mamona',
    'payments',

    'satchless.cart',
    'satchless.category',
    'satchless.checkout',
    'satchless.contact',
    'satchless.contrib.checkout.multistep',
    'satchless.contrib.checkout.singlestep',
    'satchless.contrib.delivery.percountry',
    'satchless.contrib.delivery.simplepost',
    'satchless.contrib.payment.authorizenet_provider',
    'satchless.contrib.payment.django_payments_provider',
    'satchless.contrib.payment.mamona_provider',
    'satchless.contrib.payment.stripe_provider',
    'satchless.contrib.pricing.cache',
    'satchless.contrib.pricing.simpleqty',
    'satchless.contrib.stock.singlestore',
    'satchless.contrib.tax.flatgroups',
    'satchless.delivery',
    'satchless.image',
    'satchless.order',
    'satchless.payment',
    'satchless.pricing',
    'satchless.product',
]

LANGUAGE_CODE = 'en'

LOGIN_URL = '/accounts/login/'

MANAGERS = []

MIDDLEWARE_CLASSES = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'testing.urls'

SATCHLESS_DEFAULT_CURRENCY = 'PLN'
SATCHLESS_PRICING_HANDLERS = [
    'satchless.contrib.pricing.simpleqty.SimpleQtyPricingHandler'
]
SATCHLESS_DELIVERY_PROVIDER = [
    'satchless.contrib.delivery.simplepost.PostDeliveryProvider'
]

SITE_ID = 1

TEMPLATE_DIRS = [os.path.join(os.path.dirname(__file__), 'templates')]

TEST_RUNNER = 'testing.NoseTestSuiteRunner'

USE_I18N = True