#! /usr/bin/env python
from distutils.core import setup

# dynamic retrive version number from stachless.VERSION
version_tuple = __import__('satchless').VERSION
version = ".".join([str(v) for v in version_tuple])

setup(
	name="satchless",
	author="Mirumee Labs",
	author_email="hello@mirumee.com",
	description=""" e-commerence framework for creating storefronts in django""",
	version = version,
	url = "http://satchless.com/",
	packages = ["satchless",],
)
