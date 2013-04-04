#! /usr/bin/env python
from setuptools import setup, find_packages


CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.2',
    'Programming Language :: Python :: 3.3',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
    'Topic :: Software Development :: Libraries :: Python Modules']

packages = find_packages(exclude=['doc*', 'examples*', 'tests*', 'website*'])

setup(
    name='satchless',
    author='Mirumee Software',
    author_email='hello@mirumee.com',
    description='An e-commerence framework',
    license='BSD',
    version='1.0a0',
    url='http://satchless.com/',
    packages=packages,
    classifiers=CLASSIFIERS,
    platforms=['any'],
    install_requires=['prices>=0.4,<0.5a0'],
    setup_requires=['distribute>=0.6.34'],
    test_suite='satchless.tests.suite',
    include_package_data=True,
    use_2to3=True,
    zip_safe=False)
