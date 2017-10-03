#!/usr/bin/env python
# coding: utf-8

from __future__ import unicode_literals

import sys

if sys.version_info < (2, 7):
    sys.stderr.write(("WARNING: Support for Python 2.6 will be dropped in the "
                      "1.0.0 release of MkDocs\n\n"))

# For acceptable version formats, see https://www.python.org/dev/peps/pep-0440/
__version__ = '1.0.dev'
