#! /usr/bin/env python
from setuptools import setup, find_packages


CLASSIFIERS = [
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Development Status :: 7 - Inactive',
]

setup(
    name='satchless',
    author='Mirumee Software',
    author_email='hello@mirumee.com',
    description='An e-commerce framework',
    license='BSD',
    version='1.3',
    url='https://github.com/mirumee/satchless/',
    packages=find_packages(),
    classifiers=CLASSIFIERS,
    platforms=['any'],
    install_requires=['prices>=1.0,<1.1'],
    include_package_data=True,
    zip_safe=True,
)
