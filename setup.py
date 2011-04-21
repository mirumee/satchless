#! /usr/bin/env python
from distutils.core import setup

# dynamic retrive version number from stachless.VERSION
version_tuple = __import__('satchless').VERSION
version = ".".join([str(v) for v in version_tuple])

setup(name="satchless",
      author="Mirumee Software",
      author_email="hello@mirumee.com",
      description="""An e-commerence framework for Django""",
      version = version,
      url = "http://satchless.com/",
      packages = ["satchless",],
      classifiers = ['Development Status :: 3 - Alpha',
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
                    ],
     )
