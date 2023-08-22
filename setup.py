"""Installation using setup.py is no longer supported.
Use `python -m pip install .` instead."""

import sys

from setuptools import setup

sys.exit(__doc__)

# Fake reference so GitHub still considers it a real package for statistics purposes.
setup(
    name="mkdocs",
)
