#!/usr/bin/env python
from setuptools import setup, find_packages

__doc__ = """
Templatetags to add 'here' classes to appropriate elements.

"""

version = '0.0.2'

setup(
    name='django-highlight-here',
    version=version,
    description='Templatetags to add \'here\' classes to appropriate elements.',
    author='Fusionbox programmers',
    author_email='programmers@fusionbox.com',
    keywords='django',
    long_description=__doc__,
    url='https://github.com/fusionbox/django-highlight-here',
    packages=find_packages(),
    platforms="any",
    license='BSD',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
    ],
    install_requires=['beautifulsoup4'],
    requires=['beautifulsoup4'],
)
