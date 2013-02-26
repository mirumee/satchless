#! /usr/bin/env python
from setuptools import setup, find_packages


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
    'prices >= 2012.11',
]

setup(name='satchless',
      author='Mirumee Software',
      author_email='hello@mirumee.com',
      description='An e-commerence framework for Django',
      license='BSD',
      version='2013.2',
      url='http://satchless.com/',
      packages=find_packages(exclude=['doc*', 'examples*', 'tests*',
                                      'website*']),
      include_package_data=True,
      classifiers=CLASSIFIERS,
      install_requires=REQUIREMENTS,
      platforms=['any'],
      zip_safe=False,
      tests_require=['coverage', 'nose'],
      test_suite='nose.collector')
