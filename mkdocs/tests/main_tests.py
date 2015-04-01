#!/usr/bin/env python
# coding: utf-8


import logging
import unittest

from mkdocs import main


class MainTests(unittest.TestCase):
    def test_arg_to_option(self):
        """
        Check that we parse parameters passed to mkdocs properly
        """
        arg, option = main.arg_to_option('--site-dir=dir')
        self.assertEqual('site_dir', arg)
        self.assertEqual('dir', option)
        arg, option = main.arg_to_option('--site-dir=dir-name')
        self.assertEqual('site_dir', arg)
        self.assertEqual('dir-name', option)
        arg, option = main.arg_to_option('--site-dir=dir=name')
        self.assertEqual('site_dir', arg)
        self.assertEqual('dir=name', option)
        arg, option = main.arg_to_option('--use_directory_urls')
        self.assertEqual('use_directory_urls', arg)
        self.assertEqual(True, option)

    def test_configure_logging(self):
        """
        Check that logging is configured correctly
        """
        logger = logging.getLogger('mkdocs')
        main.configure_logging({})
        self.assertEqual(logging.WARNING, logger.level)
        main.configure_logging({'verbose': True})
        self.assertEqual(logging.DEBUG, logger.level)
