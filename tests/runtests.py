#!/usr/bin/env python
import os, sys

import satchless.contrib as contrib

CONTRIB_DIR_NAME = 'django.contrib'
CONTRIB_DIR = os.path.dirname(contrib.__file__)

TEST_TEMPLATE_DIR = 'templates'

ALWAYS_INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',

    'satchless.cart',
    'satchless.category',
    'satchless.contact',
    'satchless.contrib.delivery.simplepost',
    'satchless.contrib.pricing.simpleqty',
    'satchless.contrib.tax.flatgroups',
    'satchless.delivery',
    'satchless.image',
    'satchless.order',
    'satchless.payment',
    'satchless.pricing',
    'satchless.product',
]

TESTED_APPS = [
    'satchless.cart',
    'satchless.category',
    'satchless.contact',
    'satchless.contrib.checkout.multistep',
    'satchless.contrib.checkout.singlestep',
    'satchless.contrib.delivery.simplepost',
    'satchless.contrib.pricing.simpleqty',
    'satchless.contrib.pricing.cache',
    'satchless.contrib.tax.flatgroups',
    'satchless.delivery',
    'satchless.order',
    'satchless.payment',
    'satchless.pricing',
    'satchless.product',
]

def setup(verbosity, test_modules):
    from django.conf import settings
    settings_state = {
        'INSTALLED_APPS': settings.INSTALLED_APPS,
        'ROOT_URLCONF': getattr(settings, "ROOT_URLCONF", ""),
        'TEMPLATE_DIRS': settings.TEMPLATE_DIRS,
        'USE_I18N': settings.USE_I18N,
        'LOGIN_URL': settings.LOGIN_URL,
        'LANGUAGE_CODE': settings.LANGUAGE_CODE,
        'MIDDLEWARE_CLASSES': settings.MIDDLEWARE_CLASSES,
    }

    # Redirect some settings for the duration of these tests.
    settings.INSTALLED_APPS = list(ALWAYS_INSTALLED_APPS)
    settings.ROOT_URLCONF = 'urls'
    settings.TEMPLATE_DIRS = (os.path.join(os.path.dirname(__file__),
                                           TEST_TEMPLATE_DIR),)
    settings.USE_I18N = True
    settings.LANGUAGE_CODE = 'en'
    settings.LOGIN_URL = '/accounts/login/'
    settings.MIDDLEWARE_CLASSES = (
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.common.CommonMiddleware',
    )
    settings.SITE_ID = 1
    # For testing comment-utils, we require the MANAGERS attribute
    # to be set, so that a test email is sent out which we catch
    # in our tests.
    settings.MANAGERS = ("admin@djangoproject.com",)

    # satchless default configuration
    if not hasattr(settings, 'SATCHLESS_DEFAULT_CURRENCY'):
        settings.SATCHLESS_DEFAULT_CURRENCY='PLN'
    if not hasattr(settings, 'SATCHLESS_PRICING_HANDLERS'):
        settings.SATCHLESS_PRICING_HANDLERS = ('satchless.contrib.pricing.simpleqty.SimpleQtyPricingHandler',)
    if not hasattr(settings, 'SATCHLESS_DELIVERY_PROVIDER'):
        settings.SATCHLESS_DELIVERY_PROVIDER = ('satchless.contrib.delivery.simplepost.PostDeliveryProvider',)

    # Load all the ALWAYS_INSTALLED_APPS.
    # (This import statement is intentionally delayed until after we
    # access settings because of the USE_I18N dependency.)
    from django.db.models.loading import get_apps, load_app
    get_apps()

    for module_label in test_modules:
        module_dir, module_name = module_label.rsplit('.', 1)
        # if the module was named on the command line, or
        # no modules were named (i.e., run all), import
        # this module and add it to the list to test.
        if verbosity >= 2:
            print "Importing application %s" % module_name
        mod = load_app(module_label)
        if mod:
            if module_label not in settings.INSTALLED_APPS:
                settings.INSTALLED_APPS.append(module_label)

    from django.template.loaders import app_directories
    reload(app_directories)

    return settings_state

def teardown(settings_state):
    from django.conf import settings
    # Restore the old settings.
    for key, value in settings_state.items():
        setattr(settings, key, value)

    from django.template.loaders import app_directories
    reload(app_directories)

def satchless_tests(verbosity, interactive, failfast, tested_apps):
    from django.conf import settings
    failures = 0

    from django.test.utils import get_runner
    if not hasattr(settings, 'TEST_RUNNER'):
        settings.TEST_RUNNER = 'django.test.simple.DjangoTestSuiteRunner'
    TestRunner = get_runner(settings)

    settings_state = setup(verbosity, tested_apps)
    modules_names = []
    for test_label in tested_apps:
        if '.' in test_label:
            modules_names.append(test_label.rsplit('.', 1)[1])
        else:
            modules_names.append(test_label)

    if hasattr(TestRunner, 'func_name'):
        # Pre 1.2 test runners were just functions,
        # and did not support the 'failfast' option.
        import warnings
        warnings.warn(
            'Function-based test runners are deprecated. Test runners should'
            ' be classes with a run_tests() method.',
            DeprecationWarning
        )
        failures += TestRunner(modules_names, verbosity=verbosity,
                               interactive=interactive)
    else:
        test_runner = TestRunner(verbosity=verbosity, interactive=interactive,
                                 failfast=failfast)
        failures += test_runner.run_tests(modules_names)
    teardown(settings_state)
    return failures

if __name__ == "__main__":
    from optparse import OptionParser
    usage = "%prog [options] [module module module ...]"
    parser = OptionParser(usage=usage)
    parser.add_option('-v','--verbosity', action='store', dest='verbosity',
                      default='1', type='choice', choices=['0', '1', '2', '3'],
                      help='Verbosity level; 0=minimal output, 1=normal output,'
                           ' 2=all output')
    parser.add_option('--noinput', action='store_false', dest='interactive',
                      default=True,
                      help='Tells Django to NOT prompt the user for input of'
                           ' any kind.')
    parser.add_option('--failfast', action='store_true', dest='failfast',
                      default=False,
                      help='Tells Django to stop running the test suite after'
                           ' first failed test.')
    parser.add_option('--settings',
                      help='Python path to settings module, e.g.'
                           ' "myproject.settings". If this isn\'t provided,'
                           ' the DJANGO_SETTINGS_MODULE environment variable'
                           ' will be used.')

    options, args = parser.parse_args()
    if options.settings:
        os.environ['DJANGO_SETTINGS_MODULE'] = options.settings
    elif 'DJANGO_SETTINGS_MODULE' not in os.environ:
        parser.error('DJANGO_SETTINGS_MODULE is not set in the environment'
                     ' (you can use simple settings file from'
                     ' satchless.tests.views). Set it or use --settings.')
    else:
        options.settings = os.environ['DJANGO_SETTINGS_MODULE']


    failures = satchless_tests(int(options.verbosity), options.interactive,
                               options.failfast, TESTED_APPS)

    if failures:
        sys.exit(int(failures))
