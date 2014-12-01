#!/usr/bin/env python
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="bigtrees",
    version="0.1",
    description="Python functions for computing biomass for trees",
    author="Fox Peterson",
    author_email="<fox@tinybike.net>",
    maintainer="Fox Peterson",
    maintainer_email="<fox@tinybike.net>",
    license="MIT",
    url="https://github.com/dataRonin/bigtrees",
    packages=["bigtrees"],
    install_requires=["Flask"],
    keywords = ["biomass", "trees"]
)
