import unittest
from textwrap import dedent

import yaml

from mkdocs.tests.base import load_config
from mkdocs.utils import templates


class UtilsTemplatesTests(unittest.TestCase):
    def test_script_tag(self):
        cfg_yaml = dedent(
            '''
            extra_javascript:
              - some_plain_javascript.js
              - implicitly_as_module.mjs
              - path: explicitly_as_module.mjs
                type: module
              - path: deferred_plain.js
                defer: true
              - path: scripts/async_module.mjs
                type: module
                async: true
              - path: 'aaaaaa/"my script".mjs'
                type: module
                async: true
                defer: true
              - path: plain.mjs
            '''
        )
        config = load_config(**yaml.safe_load(cfg_yaml))
        config.extra_javascript.append('plain_string.mjs')

        self.assertEqual(
            [
                str(templates.script_tag_filter({'page': None, 'base_url': 'here'}, item))
                for item in config.extra_javascript
            ],
            [
                '<script src="here/some_plain_javascript.js"></script>',
                '<script src="here/implicitly_as_module.mjs" type="module"></script>',
                '<script src="here/explicitly_as_module.mjs" type="module"></script>',
                '<script src="here/deferred_plain.js" defer></script>',
                '<script src="here/scripts/async_module.mjs" type="module" async></script>',
                '<script src="here/aaaaaa/&#34;my script&#34;.mjs" type="module" defer async></script>',
                '<script src="here/plain.mjs"></script>',
                '<script src="here/plain_string.mjs"></script>',
            ],
        )
