#!/usr/bin/env python
import os, sys

import satchless.contrib as contrib

CONTRIB_DIR_NAME = 'django.contrib'
CONTRIB_DIR = os.path.dirname(contrib.__file__)

TEST_TEMPLATE_DIR = 'templates'

ALWAYS_INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sites',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.staticfiles',

    'satchless.product',
    'satchless.cart',
    'satchless.order',
    'satchless.delivery',
    'satchless.payment',
    'satchless.pricing',
    'satchless.image',
    'satchless.contrib.delivery.simplepost',
    'satchless.contrib.pricing.simpleqty',
]

SATCHLESS_TEST_GROUPS = [
    ('satchless.contrib.checkout.multistep',
     'satchless.product',
     'satchless.cart',
     'satchless.order',
     'satchless.delivery',
     'satchless.payment',
     'satchless.pricing',
     'satchless.contrib.delivery.simplepost',
     'satchless.contrib.pricing.simpleqty',),
    ('satchless.contrib.checkout.singlestep',),
]

def setup(verbosity, test_modules):
    from django.conf import settings
    state = {
        'INSTALLED_APPS': settings.INSTALLED_APPS,
        'ROOT_URLCONF': getattr(settings, "ROOT_URLCONF", ""),
        'TEMPLATE_DIRS': settings.TEMPLATE_DIRS,
        'USE_I18N': settings.USE_I18N,
        'LOGIN_URL': settings.LOGIN_URL,
        'LANGUAGE_CODE': settings.LANGUAGE_CODE,
        'MIDDLEWARE_CLASSES': settings.MIDDLEWARE_CLASSES,
    }

    # Redirect some settings for the duration of these tests.
    settings.INSTALLED_APPS = ALWAYS_INSTALLED_APPS
    settings.ROOT_URLCONF = 'urls'
    settings.TEMPLATE_DIRS = (os.path.join(os.path.dirname(__file__), TEST_TEMPLATE_DIR),)
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
        settings.SATCHLESS_PRICING_HANDLERS = ('satchless.contrib.pricing.simpleqty.handler',)
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

    return state

def teardown(state):
    from django.conf import settings
    # Restore the old settings.
    for key, value in state.items():
        setattr(settings, key, value)

def satchless_tests(verbosity, interactive, failfast, test_groups):
    from django.conf import settings
    failures = 0

    from django.test.utils import get_runner
    if not hasattr(settings, 'TEST_RUNNER'):
        settings.TEST_RUNNER = 'django.test.simple.DjangoTestSuiteRunner'
    TestRunner = get_runner(settings)

    for test_labels in test_groups:
        state = setup(verbosity, test_labels)
        modules_names = []
        for test_label in test_labels:
            if '.' in test_label:
                modules_names.append(test_label.rsplit('.', 1)[1])
            else:
                modules_names.append(test_label)

        if hasattr(TestRunner, 'func_name'):
            # Pre 1.2 test runners were just functions,
            # and did not support the 'failfast' option.
            import warnings
            warnings.warn(
                'Function-based test runners are deprecated. Test runners should be classes with a run_tests() method.',
                DeprecationWarning
            )
            failures += TestRunner(modules_names, verbosity=verbosity, interactive=interactive)
        else:
            test_runner = TestRunner(verbosity=verbosity, interactive=interactive, failfast=failfast)
            failures += test_runner.run_tests(modules_names)
        teardown(state)
        if failures and failfast:
            return failures
    return failures

if __name__ == "__main__":
    from optparse import OptionParser
    usage = "%prog [options] [module module module ...]"
    parser = OptionParser(usage=usage)
    parser.add_option('-v','--verbosity', action='store', dest='verbosity', default='1',
        type='choice', choices=['0', '1', '2', '3'],
        help='Verbosity level; 0=minimal output, 1=normal output, 2=all output')
    parser.add_option('--noinput', action='store_false', dest='interactive', default=True,
        help='Tells Django to NOT prompt the user for input of any kind.')
    parser.add_option('--failfast', action='store_true', dest='failfast', default=False,
        help='Tells Django to stop running the test suite after first failed test.')
    parser.add_option('--settings',
        help='Python path to settings module, e.g. "myproject.settings". If this isn\'t provided, the DJANGO_SETTINGS_MODULE environment variable will be used.')

    options, args = parser.parse_args()
    if options.settings:
        os.environ['DJANGO_SETTINGS_MODULE'] = options.settings
    elif "DJANGO_SETTINGS_MODULE" not in os.environ:
        parser.error("DJANGO_SETTINGS_MODULE is not set in the environment "
                      "(you can use simple settings file from satchless.tests.views). "
                      "Set it or use --settings.")
    else:
        options.settings = os.environ['DJANGO_SETTINGS_MODULE']


    if args:
        failures = satchless_tests(int(options.verbosity), options.interactive, options.failfast, [args])
    else:
        failures = satchless_tests(int(options.verbosity), options.interactive, options.failfast,
                                   SATCHLESS_TEST_GROUPS)

    if failures:
        sys.exit(bool(failures))

