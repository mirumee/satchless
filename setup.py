#! /usr/bin/env python
from setuptools import setup, find_packages


CLASSIFIERS = [
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

setup(
    name='satchless',
    author='Mirumee Software',
    author_email='hello@mirumee.com',
    description='An e-commerence framework',
    license='BSD',
    version='1.1.1',
    url='http://satchless.com/',
    packages=find_packages(),
    classifiers=CLASSIFIERS,
    platforms=['any'],
    install_requires=['prices>=0.5,<0.6a0'],
    #setup_requires=['distribute>=0.6.34'],
    test_suite='satchless.tests.suite',
    include_package_data=True,
    use_2to3=True,
    zip_safe=True)
