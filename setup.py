#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name="imap",
      packages=find_packages(),
      package_data={"": ["*.png", "*.csv", "*.json"]})
