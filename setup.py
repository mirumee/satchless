#! /usr/bin/env python
from setuptools import setup, find_packages

# dynamic retrive version number from stachless.VERSION
version_tuple = __import__('satchless').VERSION
version = '.'.join([str(v) for v in version_tuple])

CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'Environment :: Web Environment',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.5',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Topic :: Internet :: WWW/HTTP',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
    'Topic :: Software Development :: Libraries :: Python Modules',
]

REQUIREMENTS = [
    'Django >= 1.3',
    'django-mptt >= 0.4.2',
]

EXTRAS = {
    'authorize.net payment provider': [
        'django-authorizenet >= 1.0'
    ],
    'django-payments payment provider': [
        'django-payments'
    ],
    'mamona payment provider': [
        'mamona',
    ],
}

setup(name='satchless',
      author='Mirumee Software',
      author_email='hello@mirumee.com',
      description='An e-commerence framework for Django',
      version=version,
      url='http://satchless.com/',
      packages=find_packages(exclude=['doc*', 'examples*', 'tests*',
                                      'website*']),
      include_package_data=True,
      classifiers=CLASSIFIERS,
      install_requires=REQUIREMENTS,
      extras_require=EXTRAS,
      platforms=['any'],
      zip_safe=False)
