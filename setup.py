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
     )
