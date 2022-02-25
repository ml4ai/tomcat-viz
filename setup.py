#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name="tomcat-viz",
      packages=find_packages(),
      package_data={"": ["*.png", "*.csv", "*.json"]})
