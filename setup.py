#! /usr/bin/env python
from setuptools import setup, find_packages


CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.5',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
    'Topic :: Software Development :: Libraries :: Python Modules']

packages = find_packages(exclude=['doc*', 'examples*', 'tests*', 'website*'])

setup(
    name='satchless',
    author='Mirumee Software',
    author_email='hello@mirumee.com',
    description='An e-commerence framework',
    license='BSD',
    version='2013.2a',
    url='http://satchless.com/',
    packages=packages,
    classifiers=CLASSIFIERS,
    platforms=['any'],
    install_requires=['prices>=2012.11'],
    tests_require=['coverage', 'nose'],
    test_suite='nose.collector',
    include_package_data=True,
    zip_safe=False)
