#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import ez_setup
ez_setup.use_setuptools()
from setuptools import setup
import re
import os
import sys


name = 'mkdocs'
package = 'mkdocs'
description = 'In progress.'
url = 'http://www.mkdocs.org'
author = 'Tom Christie'
author_email = 'tom@tomchristie.com'
license = 'BSD'
install_requires = [
    'Jinja2==2.7.1',
    'Markdown==2.3.1',
    'PyYAML==3.10',
    'watchdog==0.7.0',
    'ghp-import==0.4.1',
]
tests_require = [
    'coverage==3.7.1',
    'flake8==2.1.0',
]

long_description = """Work in progress."""


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("^__version__ = ['\"]([^'\"]+)['\"]", init_py, re.MULTILINE).group(1)


def get_packages(package):
    """
    Return root package and all sub-packages.
    """
    return [dirpath
            for dirpath, dirnames, filenames in os.walk(package)
            if os.path.exists(os.path.join(dirpath, '__init__.py'))]


def get_package_data(package):
    """
    Return all files under the root package, that are not in a
    package themselves.
    """
    walk = [(dirpath.replace(package + os.sep, '', 1), filenames)
            for dirpath, dirnames, filenames in os.walk(package)
            if not os.path.exists(os.path.join(dirpath, '__init__.py'))]

    filepaths = []
    for base, filenames in walk:
        filepaths.extend([os.path.join(base, filename)
                          for filename in filenames])
    return {package: filepaths}


if sys.argv[-1] == 'publish':
    os.system("python setup.py sdist upload")
    args = {'version': get_version(package)}
    print("You probably want to also tag the version now:")
    print("  git tag -a %(version)s -m 'version %(version)s'" % args)
    print("  git push --tags")
    sys.exit()


setup(
    name=name,
    version=get_version(package),
    url=url,
    license=license,
    description=description,
    long_description=long_description,
    author=author,
    author_email=author_email,
    packages=get_packages(package),
    package_data=get_package_data(package),
    install_requires=install_requires,
    tests_require=tests_require,
    test_suite="test",
    entry_points={
        'console_scripts': [
            'mkdocs = mkdocs.mkdocs:main_entry_point',
            ],
        },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
