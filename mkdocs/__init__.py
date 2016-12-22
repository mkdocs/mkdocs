#!/usr/bin/env python
# coding: utf-8

from __future__ import unicode_literals

import sys

if sys.version_info < (2, 7):
    sys.stderr.write(("WARNING: Support for Python 2.6 will be dropped in the "
                      "1.0.0 release of MkDocs\n\n"))

__version__ = '0.16.1'
