#!/usr/bin/env python

from setuptools import setup, find_packages
import re
import os
import sys


long_description = (
    "`elstir` is a fork of `mkdocs`. `mkdocs` is a fast, simple and downright gorgeous static site generator "
    "that's geared towards building project documentation. Documentation "
    "source files are written in Markdown, and configured with a single YAML "
    "configuration file."
)


def get_version(package):
    """Return package version as listed in `__version__` in `__init__.py`."""
    with open(os.path.join(package, '__init__.py')) as f:
        init_py = f.read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


# def get_packages(package):
#     """Return root package and all sub-packages."""
#     return [dirpath
#             for dirpath, dirnames, filenames in os.walk(package)
#             if os.path.exists(os.path.join(dirpath, '__init__.py'))]


# if sys.argv[-1] == 'publish':
#     os.system("python setup.py sdist bdist_wheel")
#     os.system("twine upload dist/*")
#     print("You probably want to also tag the version now:")
#     print("  git tag -a {0} -m 'version {0}'".format(__version__))
#     print("  git push --tags")
#     sys.exit()


__version__ = get_version("./src/elstir")
setup(
    name="elstir",
    version=__version__,
    url='https://claudioperez.github.io/elstir',
    license='BSD',
    description='Project documentation with Markdown.',
    long_description=long_description,
    author='Claudio Perez',
    author_email='claudio_perez@berkeley.edu',  
    packages=find_packages("src"),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=[
        'click>=3.3',
        'Jinja2>=2.10.1',
        'livereload>=2.5.1',
        'lunr[languages]==0.5.8',  # must support lunr.js version included in search
        'Markdown>=3.2.1',
        'PyYAML>=3.10',
        'tornado>=5.0'
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'elstir = elstir.__main__:cli',
        ],
        'elstir.themes': [
            'elstir = elstir.themes.elstir',
            'readthedocs = elstir.themes.readthedocs',
            'berkeley = elstir.themes.berkeley',
            'odette = elstir.themes.odette',
        ],
        'elstir.plugins': [
            'search = elstir.contrib.search:SearchPlugin',
            'exclude = elstir.contrib.exclude:Exclude',
        ],
    },
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Documentation",
        "Topic :: Text Processing",
        "Topic :: Text Processing :: Markup",
        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Text Processing :: Markup :: LaTeX",
        "Topic :: Text Processing :: Markup :: Markdown",
    ],
    zip_safe=False,
)

