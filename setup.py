"""Set up for the edX Search CAG Support package."""

from setuptools import setup

description = 'A hack package to add Course Access Groups / `has_access` support for edx-search.'

setup(
    name='tahoe-edx-search',
    version='0.1.0',
    description=description,
    long_description=description,
    long_description_content_type="text/markdown",
    packages=[
        'tahoe_edx_search',
    ],
)
